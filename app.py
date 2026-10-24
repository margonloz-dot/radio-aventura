"""Radio Aventura: aplicación local, sólo biblioteca estándar de Python 3.10+."""
from __future__ import annotations

import argparse
import copy
import json
import math
import os
from pathlib import Path
import random
import secrets
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import webbrowser

ROOT = Path(__file__).resolve().parent
COURSE = json.loads((ROOT / 'curso.json').read_text(encoding='utf-8'))
LESSONS = {x['id']: x for x in COURSE['lessons']}
ORDER = list(LESSONS)
CHAPTERS = {x['id']: x for x in COURSE['chapters']}
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.RLock()
DATA = ROOT / 'datos'
STATE_PATH = DATA / 'progreso.json'


def fresh_state():
    return {'version': 1, 'lessons': {}, 'bosses': {}, 'current': ORDER[0],
            'created': time.strftime('%Y-%m-%d'), 'updated': ''}


def load_state():
    if not STATE_PATH.exists():
        return fresh_state()
    for p in [STATE_PATH, DATA / 'progreso.anterior.json']:
        try:
            obj = json.loads(p.read_text(encoding='utf-8'))
            if obj.get('version') != 1 or not isinstance(obj.get('lessons'), dict):
                raise ValueError('Formato de progreso incompatible')
            return obj
        except (OSError, ValueError, TypeError):
            continue
    damaged = DATA / f'progreso.no-legible-{time.time_ns()}.json'
    try:
        damaged.write_bytes(STATE_PATH.read_bytes())
    except OSError:
        pass
    print('El progreso no se pudo leer. Se preservó el archivo y se inicia una partida nueva.')
    return fresh_state()


STATE = load_state()


def save_state():
    DATA.mkdir(exist_ok=True)
    STATE['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
    tmp = DATA / 'progreso.tmp'
    tmp.write_text(json.dumps(STATE, ensure_ascii=False, indent=2), encoding='utf-8')
    if STATE_PATH.exists():
        (DATA / 'progreso.anterior.json').write_bytes(STATE_PATH.read_bytes())
    os.replace(tmp, STATE_PATH)


def done(lid):
    s = STATE['lessons'].get(lid, {})
    return all(s.get(x, False) for x in ['read', 'lab', 'quiz'])


def unlocked(lid):
    i = ORDER.index(lid)
    if i == 0:
        return True
    previous = ORDER[i-1]
    if not done(previous):
        return False
    ch = LESSONS[lid]['chapter']
    old = LESSONS[previous]['chapter']
    return ch == old or bool(STATE['bosses'].get(old))


def public_state():
    completed = sum(done(lid) for lid in ORDER)
    xp = sum(5 * bool(s.get('read')) + 15 * bool(s.get('lab')) + 30 * bool(s.get('quiz'))
             for lid, s in STATE['lessons'].items() if lid in LESSONS)
    xp += sum(100 for k, v in STATE['bosses'].items() if k in CHAPTERS and v)
    s = copy.deepcopy(STATE)
    s.update(completed=completed, xp=xp, unlocked=[lid for lid in ORDER if unlocked(lid)],
             total=len(ORDER), rank=['Aprendiz de señales', 'Explorador del espectro',
             'Constructor de enlaces', 'Arquitecto de radio'][min(3, completed * 4 // len(ORDER))])
    return s


def award(lid, stage):
    previous = copy.deepcopy(STATE)
    s = STATE['lessons'].setdefault(lid, {})
    new = not s.get(stage, False)
    s[stage] = True
    STATE['current'] = lid
    try:
        save_state()
    except OSError:
        STATE.clear()
        STATE.update(previous)
        raise
    return new


def lab_config(lid):
    """Objetivos por sección; el motor matemático corre en Python."""
    ch = LESSONS[lid]['chapter']
    i = int(lid.split('.')[1])
    if ch == '1':
        f = [30, 60, 100, 150, 300, 600, 900][(i-1) % 7]
        return dict(kind='wave', title='La baliza de longitud de onda', label='Frecuencia (MHz)',
                    min=10, max=1000, step=1, initial=400, target=300/f,
                    goal=f'Consigue una longitud de onda de {300/f:.3g} m (± 2 %).',
                    hint=f'λ = 300 / f, con f en MHz. Despeja f = 300 / λ.', unit='MHz')
    if ch in ['2', '12']:
        angle = [0, 30, 45, 60][i % 4]
        target = 100 * math.cos(math.radians(angle))**2
        return dict(kind='polarization', title='Alinea las antenas', label='Desalineación (grados)',
                    min=0, max=90, step=1, initial=80, target=target,
                    goal=f'Entrega {target:.1f} % de la potencia por alineación (± 2 puntos).',
                    hint='Para dos polarizaciones lineales, la fracción de potencia es cos²(θ).', unit='°')
    if ch in ['3', '7']:
        d = [1, 2, 4, 6, 8][i % 5]
        target = 20 + 12 + 12 - (32.44 + 20*math.log10(2400) + 20*math.log10(d)) - 2
        return dict(kind='link', title='Reconecta la estación remota', label='Distancia (km)',
                    min=.2, max=10, step=.1, initial=9, target=target,
                    goal=f'Obtén Pr = {target:.1f} dBm (± 0.5 dB). TX=20 dBm; antenas=12 dBi cada una; pérdidas=2 dB; f=2400 MHz.',
                    hint='Pr = Pt + Gt + Gr − L − FSPL. Acercar las estaciones reduce FSPL.', unit='km')
    if ch == '4':
        b = [10, 50, 100, 200, 500][i % 5]
        target = 10*math.log10(1.380649e-23*290*b*1000)+30
        return dict(kind='noise', title='Escucha debajo del ruido', label='Ancho de banda (kHz)',
                    min=1, max=1000, step=1, initial=800, target=target,
                    goal=f'Sitúa el ruido térmico en {target:.1f} dBm (± 0.25 dB), a 290 K.',
                    hint='N = kTB. Reducir el ancho de banda reduce la potencia de ruido; también puede cortar información.', unit='kHz')
    if ch == '5':
        m = [.2,.4,.6,.8,1][i % 5]
        return dict(kind='am', title='Transporta una señal sin deformarla', label='Índice de modulación AM',
                    min=0, max=1.5, step=.01, initial=1.3, target=m,
                    goal=f'Obtén un factor de amplitud mínimo de {1-m:.2f} y máximo de {1+m:.2f} (± 0.03), con A=1.',
                    hint='s(t) = [1 + μ cos(2πfmt)] cos(2πfct). El factor con signo varía entre 1−μ y 1+μ. La envolvente física es su valor absoluto; si μ>1 hay sobremodulación.', unit='')
    if ch in ['6', 'B']:
        m = [2,4,16,64][i % 4]
        target = math.log2(m)
        return dict(kind='digital', title='El mensajero de símbolos', label='Estados de la constelación (M)',
                    values=[2,4,16,64], initial=2, target=target,
                    goal=f'Transporta {target:.0f} bits por símbolo. Después observa qué ocurre si reduces la separación entre puntos.',
                    hint='Un símbolo entre M posibilidades representa log₂(M) bits. Más bits por símbolo exigen mejor SNR para la misma BER.', unit='estados')
    if ch in ['8', '9']:
        z = [25,50,75,100][i % 4]
        target = abs((z-50)/(z+50))**2 * 100
        return dict(kind='match', title='Domina la reflexión', label='Carga resistiva (ohm)',
                    min=10, max=150, step=1, initial=140, target=target,
                    goal=f'Consigue {target:.2f} % de potencia reflejada (± 0.4 puntos), con Z₀=50 Ω.',
                    hint='Γ=(ZL−Z₀)/(ZL+Z₀); potencia reflejada=|Γ|². El laboratorio usa cargas reales, sin reactancia.', unit='Ω')
    if ch == '10':
        gain = [5,10,15,20,25][i % 5]
        return dict(kind='gain', title='Amplifica con propósito', label='Ganancia (dB)',
                    min=0, max=40, step=.5, initial=2, target=-60+gain,
                    goal=f'Lleva una entrada de −60 dBm a {(-60+gain):.1f} dBm (± 0.25 dB).',
                    hint='En un amplificador lineal adaptado, Pout[dBm]=Pin[dBm]+G[dB]. No se modelan compresión ni ruido en este experimento.', unit='dB')
    if ch == '11':
        pin = [-30,-25,-20,-15,-10][i % 5]
        target = 2*(0-pin)
        return dict(kind='linearity', title='Mantén a raya los productos espurios', label='Potencia por tono de entrada (dBm)',
                    min=-40, max=-5, step=.5, initial=-5, target=target,
                    goal=f'Consigue una separación fundamental–IM3 de {target:.0f} dB (± 1 dB); IIP3=0 dBm.',
                    hint='En el modelo de pequeña señal de dos tonos: Δ=2(IIP3−Pin). El IP3 es una extrapolación, no una potencia de operación.', unit='dBm')
    if ch == '13':
        target = [-3.0103,-6.9897,-10,-12.3045][i % 4]
        return dict(kind='filter', title='La puerta de las frecuencias', label='Frecuencia de la señal / frecuencia de corte',
                    min=.1, max=5, step=.01, initial=4, target=target,
                    goal=f'Obtén una respuesta de {target:.2f} dB (± 0.15 dB) en un pasabajas RC de primer orden.',
                    hint='H[dB]=−10 log₁₀(1+(f/fc)²). A f=fc la caída es aproximadamente 3 dB.', unit='× fc')
    if ch in ['14', '15']:
        fi = [10,20,30,40,50][i % 5]
        return dict(kind='mixer', title='Sintoniza la frecuencia intermedia', label='Oscilador local (MHz)',
                    min=50, max=150, step=1, initial=100, target=fi,
                    goal=f'Convierte RF=100 MHz a FI={fi} MHz. Existen dos soluciones posibles.',
                    hint='FI=|RF−LO|. Un mezclador real también produce suma, imagen y otros productos; el filtro selecciona el deseado.', unit='MHz')
    if ch == '16':
        target = [80,100,120,140,160][i % 5]
        return dict(kind='pll', title='Engancha la baliza de referencia', label='Divisor entero N',
                    min=1, max=30, step=1, initial=3, target=target,
                    goal=f'Sintetiza {target} MHz con referencia de 10 MHz y divisor de referencia R=1.',
                    hint='En enganche y para un PLL entero ideal: fout=N·fref/R. Este laboratorio no modela el transitorio de adquisición.', unit='')
    if ch == '17':
        target = [20,40,60,80][i % 4]
        return dict(kind='pa', title='El transmisor eficiente', label='Potencia de RF de salida (W)',
                    min=1, max=95, step=1, initial=10, target=target,
                    goal=f'Logra {target} % de eficiencia de drenador con consumo DC fijo de 100 W.',
                    hint='ηD=PRF/PDC. La diferencia se convierte principalmente en calor. Eficiencia y linealidad deben evaluarse juntas.', unit='W')
    if ch == '18':
        target = [5,10,15,20,25][i % 5]
        return dict(kind='sampling', title='El puente al dominio digital', label='Frecuencia de muestreo (kS/s)',
                    min=10, max=150, step=1, initial=20, target=target,
                    goal=f'Para un tono de 35 kHz, obtén un alias de {target} kHz (± 0.1 kHz). Explora también fs>70 kS/s para evitar alias.',
                    hint='El tono observado se pliega al intervalo 0…fs/2. Esta demostración de alias no representa un diseño completo de submuestreo.', unit='kS/s')
    target = [60,70,80,90][i % 4]
    return dict(kind='path', title='Cartografía la pérdida media', label='Distancia (m)',
                min=1, max=100, step=.1, initial=10, target=target,
                goal=f'Obtén {target} dB de pérdida media. L(d₀=1 m)=40 dB y n=3.',
                hint='L(d)=40+10·3·log₁₀(d/1). Es un modelo medio; no representa cada fluctuación del canal.', unit='m')


def simulate(kind, x):
    if kind == 'wave':
        v=300/x; return v, f'λ = {v:.3f} m', 'Una frecuencia mayor produce una longitud de onda menor.'
    if kind == 'polarization':
        v=100*math.cos(math.radians(x))**2
        return v, f'Potencia por alineación: {v:.2f} %', 'Antenas lineales ideales. Las pérdidas reales y la propagación se evalúan aparte.'
    if kind == 'link':
        loss=32.44+20*math.log10(2400)+20*math.log10(x); v=42-loss
        return v, f'Pr = {v:.2f} dBm', f'FSPL={loss:.2f} dB. Modelo de espacio libre: campo lejano, visibilidad y antenas alineadas.'
    if kind == 'noise':
        v=10*math.log10(1.380649e-23*290*x*1000)+30
        return v, f'N = {v:.2f} dBm', 'Potencia disponible en carga adaptada; 290 K; ancho de banda rectangular equivalente.'
    if kind == 'am': return x, f'A(t): {1-x:.2f} … {1+x:.2f}', 'Sobremodulación: A(t) cambia de signo. La envolvente física es abs(A(t)).' if x>1 else 'A(t) no cambia de signo; coincide con la envolvente del tono normalizado.'
    if kind == 'digital':
        v=math.log2(x);return v, f'{v:.0f} bits/símbolo', f'A 1000 símbolos/s: {v*1000:.0f} bit/s antes de codificación. La BER depende de la SNR.'
    if kind == 'match':
        gamma=(x-50)/(x+50);v=gamma**2*100
        return v,f'Reflejada: {v:.2f} %',f'Γ={gamma:.3f}; VSWR={(1+abs(gamma))/(1-abs(gamma)):.2f}. Carga puramente resistiva.'
    if kind == 'gain': return -60+x, f'Pout = {-60+x:.1f} dBm', f'Ganancia de potencia lineal: {10**(x/10):.1f} veces.'
    if kind == 'linearity':return -2*x,f'Separación IM3: {-2*x:.1f} dB','Aumentar 1 dB cada tono aumenta el IM3 aproximadamente 3 dB en el modelo cúbico.'
    if kind == 'filter':
        v=-10*math.log10(1+x*x);return v,f'H = {v:.2f} dB','Filtro RC de primer orden: −20 dB/década asintóticos; no se calcula el filtro LC completo.'
    if kind == 'mixer':return abs(100-x),f'FI = {abs(100-x):.0f} MHz',f'Producto suma: {100+x:.0f} MHz. RF deseada fijada en 100 MHz.'
    if kind == 'pll':return 10*x,f'fout = {10*x:.0f} MHz','Modelo ideal en enganche. El ruido de fase y los espurios requieren análisis adicional.'
    if kind == 'pa':return x,f'ηD = {x:.0f} %',f'Calor estimado: {100-x:.0f} W; no incluye potencia RF de entrada ni pérdidas auxiliares.'
    if kind == 'sampling':
        v=abs((35+x/2)%x-x/2);return v,f'Tono observado: {v:.1f} kHz',f'Nyquist: {x/2:.1f} kHz. fs>70 kS/s conserva el tono de 35 kHz con filtrado previo adecuado.'
    v=40+30*math.log10(x);return v,f'Pérdida media = {v:.2f} dB','Modelo logarítmico con exponente n=3; no es Hata ni una predicción medida del sitio.'


def public_course():
    result=copy.deepcopy(COURSE)
    for lesson in result['lessons']:
        lesson.pop('answer',None)
        lesson.pop('explanation',None)
        lesson['lab']=lab_config(lesson['id'])
        lesson['lab'].pop('target',None)
    result['token']=TOKEN
    return result


def check_lab(lid, x):
    cfg=lab_config(lid)
    if not math.isfinite(x): raise ValueError('Introduce un valor finito.')
    if 'values' in cfg:
        if x not in cfg['values']: raise ValueError('Escoge uno de los estados disponibles.')
    elif x < cfg['min'] or x > cfg['max']:
        raise ValueError('El valor está fuera del intervalo del laboratorio.')
    value,label,detail=simulate(cfg['kind'],x)
    tolerance={'wave':abs(cfg['target'])*.02,'polarization':2,'link':.5,'noise':.25,
               'am':.03,'digital':.01,'match':.4,'gain':.25,'linearity':1,'filter':.15,
               'mixer':.01,'pll':.01,'pa':.01,'sampling':.1,'path':.5}[cfg['kind']]
    return dict(value=value,label=label,detail=detail,success=abs(value-cfg['target'])<=tolerance+1e-9)


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args): pass

    def send(self,status,body,ctype='application/json; charset=utf-8',extra=None):
        if isinstance(body,(dict,list)):body=json.dumps(body,ensure_ascii=False).encode('utf-8')
        elif isinstance(body,str):body=body.encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type',ctype)
        self.send_header('Content-Length',str(len(body)))
        self.send_header('Cache-Control','no-store')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('Referrer-Policy','same-origin')
        self.send_header('X-Frame-Options','SAMEORIGIN')
        if extra:
            for k,v in extra.items():self.send_header(k,v)
        self.end_headers()
        try:self.wfile.write(body)
        except (BrokenPipeError,ConnectionResetError):pass

    def valid_host(self):
        return self.headers.get('Host') in [f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}']

    def do_GET(self):
        if not self.valid_host():return self.send(403,{'error':'Acceso sólo local.'})
        url=urlparse(self.path);path=url.path
        if path=='/api/course':return self.send(200,public_course())
        if path=='/api/state':
            with LOCK:return self.send(200,public_state())
        if path=='/api/export':
            with LOCK:return self.send(200,copy.deepcopy(STATE),extra={'Content-Disposition':'attachment; filename="radio-aventura-progreso.json"'})
        if path=='/api/source':
            lid=parse_qs(url.query).get('id',[''])[0]
            if lid not in LESSONS:return self.send(404,{'error':'Sección desconocida.'})
            return self.send(200,json.loads((ROOT/'fuentes.json').read_text(encoding='utf-8')).get(lid,{}))
        if path=='/api/search':
            q=parse_qs(url.query).get('q',[''])[0].strip().casefold()[:100]
            if len(q)<3:return self.send(200,[])
            hits=[]
            pages=json.loads((ROOT/'libro_busqueda.json').read_text(encoding='utf-8'))
            for page in pages:
                at=page['text'].casefold().find(q)
                if at>=0:
                    hits.append({'pdf_page':page['pdf_page'],'page':page['page'],
                                 'excerpt':page['text'][max(0,at-100):at+220]})
                    if len(hits)==30:break
            return self.send(200,hits)
        if path=='/libro.pdf':
            p=ROOT/'libro'/'RadioSystemsEngineeringRev1stEd.pdf'
            if p.exists():return self.send(200,p.read_bytes(),'application/pdf')
            return self.send(404,'No se encontró el PDF en la carpeta libro.','text/plain; charset=utf-8')
        files={'/':'index.html','/style.css':'style.css','/game.js':'game.js'}
        ctypes={'/':'text/html; charset=utf-8','/style.css':'text/css; charset=utf-8','/game.js':'text/javascript; charset=utf-8'}
        if path in files:return self.send(200,(ROOT/files[path]).read_bytes(),ctypes[path])
        if path=='/favicon.ico':return self.send(204,b'','image/x-icon')
        self.send(404,{'error':'Ruta inexistente.'})

    def do_POST(self):
        if not self.valid_host() or self.headers.get('X-Radio-Token')!=TOKEN:
            return self.send(403,{'error':'Sesión local inválida. Recarga la página.'})
        origin=self.headers.get('Origin')
        if origin and origin not in [f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}']:
            return self.send(403,{'error':'Origen no permitido.'})
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=60000:raise ValueError('Solicitud demasiado grande o vacía.')
            body=json.loads(self.rfile.read(length))
            if not isinstance(body,dict):raise ValueError('Se esperaba un objeto de datos.')
            with LOCK:result=self.action(urlparse(self.path).path,body)
            return self.send(200,result)
        except (ValueError,KeyError,TypeError) as e:return self.send(400,{'error':str(e)})
        except OSError:return self.send(500,{'error':'No fue posible guardar. Revisa el permiso de escritura de la carpeta datos.'})

    def action(self,path,body):
        lid=body.get('id','')
        if path=='/api/note':
            note=body.get('note','')
            if not isinstance(note,str) or len(note)>12000:raise ValueError('Las notas admiten hasta 12000 caracteres.')
            previous=copy.deepcopy(STATE)
            STATE['notes']=note
            try:save_state()
            except OSError:
                STATE.clear();STATE.update(previous);raise
            return dict(state=public_state())
        if path=='/api/boss':
            ch=body.get('chapter')
            if ch not in CHAPTERS:raise ValueError('Capítulo desconocido.')
            ids=[l['id'] for l in COURSE['lessons'] if l['chapter']==ch]
            if not all(done(x) for x in ids):raise ValueError('Completa todas las misiones de este sector.')
            picked=[ids[0],ids[len(ids)//2],ids[-1]]
            answers=body.get('answers',[])
            if len(answers)!=3:raise ValueError('Responde las tres preguntas de integración.')
            results=[{'success':answers[i]==LESSONS[x]['answer'],'explanation':LESSONS[x]['explanation']} for i,x in enumerate(picked)]
            success=all(r['success'] for r in results)
            new=False
            if success:
                previous=copy.deepcopy(STATE)
                new=not STATE['bosses'].get(ch)
                STATE['bosses'][ch]=True
                try:save_state()
                except OSError:
                    STATE.clear();STATE.update(previous);raise
            return dict(success=success,results=results,new=new,state=public_state())
        if lid not in LESSONS:raise ValueError('Misión desconocida.')
        if path=='/api/simulate':return check_lab(lid,float(body.get('value')))
        if not unlocked(lid):raise ValueError('Esta misión se desbloquea al completar la anterior y su reto de sector.')
        if path=='/api/read':
            new=award(lid,'read');return dict(new=new,state=public_state())
        if path=='/api/lab':
            if not STATE['lessons'].get(lid,{}).get('read'):raise ValueError('Primero termina la explicación.')
            result=check_lab(lid,float(body.get('value')))
            result['new']=award(lid,'lab') if result['success'] else False
            result['state']=public_state();return result
        if path=='/api/quiz':
            if not STATE['lessons'].get(lid,{}).get('lab'):raise ValueError('Primero completa la práctica.')
            lesson=LESSONS[lid];success=body.get('answer')==lesson['answer']
            new=award(lid,'quiz') if success else False
            return dict(success=success,explanation=lesson['explanation'],new=new,state=public_state())
        raise ValueError('Acción desconocida.')


def main():
    parser=argparse.ArgumentParser(description='Radio Aventura — aprende ingeniería de radio localmente.')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    if not 1024<=args.port<=65535:parser.error('El puerto debe estar entre 1024 y 65535.')
    # Una segunda apertura reutiliza la instancia local del mismo programa.
    import urllib.request
    for port in range(args.port,min(args.port+10,65536)):
        try:
            with urllib.request.urlopen(f'http://127.0.0.1:{port}/api/course',timeout=.3) as res:
                existing=json.load(res)
            if existing.get('app_id')==COURSE['app_id']:
                if not args.no_browser:webbrowser.open(f'http://127.0.0.1:{port}')
                print(f'Radio Aventura ya está abierta: http://127.0.0.1:{port}')
                return
        except Exception:pass
        try:server=ThreadingHTTPServer(('127.0.0.1',port),Handler);break
        except OSError:continue
    else:raise SystemExit('No hay un puerto local libre. Usa: python app.py --port 9000')
    address=f'http://127.0.0.1:{server.server_port}'
    print(f'\nRADIO AVENTURA\n{address}\n{len(ORDER)} misiones · 20 sectores · Sin conexión a Internet\n')
    print('Mantén esta ventana abierta. Para salir, presiona Ctrl+C o cierra esta ventana.\n')
    if not args.no_browser:threading.Timer(.6,lambda:webbrowser.open(address)).start()
    try:server.serve_forever()
    except KeyboardInterrupt:print('\nTu avance está guardado. ¡Hasta la próxima transmisión!')
    finally:server.server_close()


if __name__=='__main__':main()
