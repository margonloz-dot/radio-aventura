"""Verificaciones de cálculos, evaluación, progresión, HTTP y recuperación de datos.
Ejecutar: python -m unittest -v test_radio.py
Las pruebas usan una carpeta temporal; no modifican tu partida.
"""
import importlib.util
import json
import math
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.request import Request, urlopen
from urllib.error import HTTPError

spec=importlib.util.spec_from_file_location('radio_test_app',Path(__file__).with_name('app.py'))
app=importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)


class RadioTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.original=(app.DATA,app.STATE_PATH,app.STATE)
        app.DATA=Path(self.temp.name)
        app.STATE_PATH=app.DATA/'progreso.json'
        app.STATE=app.fresh_state()

    def tearDown(self):
        app.DATA,app.STATE_PATH,app.STATE=self.original
        self.temp.cleanup()

    def test_curriculum_covers_toc_and_source(self):
        self.assertEqual(len(app.LESSONS),166)
        self.assertEqual(len(app.CHAPTERS),20)
        self.assertEqual(len(set(app.ORDER)),166)
        sources=json.loads((app.ROOT/'fuentes.json').read_text(encoding='utf8'))
        pages=json.loads((app.ROOT/'libro_busqueda.json').read_text(encoding='utf8'))
        self.assertEqual(len(pages),531)
        self.assertEqual(set(sources),set(app.LESSONS))
        self.assertEqual(app.LESSONS['1.1']['pdf_page'],15)
        self.assertEqual(app.LESSONS['B.8']['pdf_page'],513)
        for lid,l in app.LESSONS.items():
            with self.subTest(lid=lid):
                self.assertIn(lid,sources[lid]['text'][:500])
                self.assertGreater(len(l['what'])+len(l['how'])+len(l['use']),300)
                self.assertEqual(len(l['options']),3)
                self.assertEqual(len(set(l['options'])),3)
                self.assertIn(l['answer'],range(3))
        p=app.public_course()
        self.assertTrue(all('answer' not in l and 'explanation' not in l and 'target' not in l['lab'] for l in p['lessons']))

    def test_known_physics_reference_values(self):
        self.assertAlmostEqual(app.simulate('wave',100)[0],3)
        self.assertAlmostEqual(app.simulate('polarization',45)[0],50)
        self.assertAlmostEqual(app.simulate('polarization',90)[0],0)
        self.assertAlmostEqual(app.simulate('noise',1)[0],-143.975187,places=5)
        self.assertAlmostEqual(app.simulate('link',1)[0],-58.0442248,places=5)
        self.assertAlmostEqual(app.simulate('match',100)[0],100/9)
        self.assertAlmostEqual(app.simulate('filter',1)[0],-3.0102999566)
        self.assertEqual(app.simulate('digital',64)[0],6)
        self.assertEqual(app.simulate('mixer',90)[0],10)
        self.assertEqual(app.simulate('mixer',110)[0],10)
        self.assertEqual(app.simulate('sampling',50)[0],15)
        self.assertEqual(app.simulate('sampling',100)[0],35)
        self.assertEqual(app.simulate('pll',12)[0],120)

    def test_spanish_mexico_reading_has_full_coverage_and_preserves_math(self):
        sources=json.loads((app.ROOT/'fuentes.json').read_text(encoding='utf8'))
        import hashlib,re
        for lid,s in sources.items():
            with self.subTest(lid=lid):
                self.assertTrue(s.get('text_es_mx'))
                self.assertTrue(s.get('text_en_clean'))
                self.assertTrue(s.get('title_es_mx'))
                self.assertEqual(s['translation_meta']['language'],'es-MX')
                self.assertEqual(s['translation_meta']['source_sha256'],hashlib.sha256(s['text'].encode()).hexdigest())
                self.assertFalse(re.search(r'ZX\s*\d+',s['text_es_mx']))
                self.assertEqual(s['text_es_mx'],'\n\n'.join(b['text'] for b in s['blocks_es_mx']))
                for block in s['blocks_es_mx']:
                    self.assertGreaterEqual(block['pdf_page'],s['start_pdf_page'])
                    self.assertLessEqual(block['pdf_page'],s['end_pdf_page'])
        self.assertIn('La radio consiste en utilizar campos electromagnéticos',sources['1.1']['text_es_mx'])
        self.assertIn('λf = c',sources['1.1']['text_es_mx'])

    def test_all_lab_goals_are_reachable_with_visible_control(self):
        for lid in app.ORDER:
            c=app.lab_config(lid)
            values=c.get('values') or [round(c['min']+i*c['step'],8) for i in range(round((c['max']-c['min'])/c['step'])+1)]
            with self.subTest(lid=lid):
                self.assertTrue(any(app.check_lab(lid,x)['success'] for x in values))
                for x in [float('nan'),float('inf'),-999999]:
                    with self.assertRaises(ValueError):app.check_lab(lid,x)

    def test_save_and_recover_corrupt_main_file(self):
        app.award('1.1','read')
        app.award('1.1','lab')
        app.STATE_PATH.write_text('{not valid json',encoding='utf8')
        recovered=app.load_state()
        self.assertTrue(recovered['lessons']['1.1']['read'])
        app.STATE_PATH.write_text('broken',encoding='utf8')
        (app.DATA/'progreso.anterior.json').write_text('broken',encoding='utf8')
        recovered=app.load_state()
        self.assertEqual(recovered['lessons'],{})
        self.assertTrue(list(app.DATA.glob('progreso.no-legible-*.json')))

    def test_http_full_campaign_and_replay_idempotence(self):
        server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        address=f'http://127.0.0.1:{server.server_port}'
        def request(path,data=None,token=True):
            headers={'X-Radio-Token':app.TOKEN} if token else {}
            if data is not None:headers['Content-Type']='application/json'
            req=Request(address+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
            with urlopen(req,timeout=15) as r:return json.load(r)
        try:
            with self.assertRaises(HTTPError) as e:request('/api/read',{'id':'1.2'})
            self.assertEqual(e.exception.code,400)
            with self.assertRaises(HTTPError) as e:request('/api/read',{'id':'1.1'},token=False)
            self.assertEqual(e.exception.code,403)
            with self.assertRaises(HTTPError):request('/api/quiz',{'id':'1.1','answer':app.LESSONS['1.1']['answer']})
            for ch in app.CHAPTERS:
                ids=[i for i in app.ORDER if app.LESSONS[i]['chapter']==ch]
                for lid in ids:
                    request('/api/read',{'id':lid})
                    c=app.lab_config(lid)
                    values=c.get('values') or [round(c['min']+i*c['step'],8) for i in range(round((c['max']-c['min'])/c['step'])+1)]
                    solution=next(x for x in values if app.check_lab(lid,x)['success'])
                    self.assertTrue(request('/api/lab',{'id':lid,'value':solution})['success'])
                    correct=app.LESSONS[lid]['answer']
                    before=request('/api/state')['xp']
                    self.assertFalse(request('/api/quiz',{'id':lid,'answer':(correct+1)%3})['success'])
                    self.assertEqual(request('/api/state')['xp'],before)
                    self.assertTrue(request('/api/quiz',{'id':lid,'answer':correct})['success'])
                    once=request('/api/state')['xp']
                    self.assertFalse(request('/api/quiz',{'id':lid,'answer':correct})['new'])
                    self.assertEqual(request('/api/state')['xp'],once)
                picked=[ids[0],ids[len(ids)//2],ids[-1]]
                # El siguiente sector aún espera el reto del anterior.
                idx=app.ORDER.index(ids[-1])
                if idx+1<len(app.ORDER):self.assertFalse(app.unlocked(app.ORDER[idx+1]))
                result=request('/api/boss',{'chapter':ch,'answers':[app.LESSONS[i]['answer'] for i in picked]})
                self.assertTrue(result['success'])
            s=request('/api/state');self.assertEqual(s['completed'],166);self.assertEqual(s['xp'],10300)
            request('/api/note',{'note':'Prueba de persistencia: señal y ruido.'})
            loaded=app.load_state();self.assertEqual(loaded['notes'],'Prueba de persistencia: señal y ruido.')
            self.assertEqual(len(loaded['bosses']),20)
            self.assertIn('1.1',request('/api/source?id=1.1')['text'])
            self.assertTrue(request('/api/search?q=orthogonal'))
            with self.assertRaises(HTTPError):
                req=Request(address+'/api/state',headers={'Host':'evil.example'})
                urlopen(req,timeout=5)
        finally:server.shutdown();server.server_close();thread.join()


if __name__=='__main__':unittest.main(verbosity=2)
