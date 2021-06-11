import time,ctypes,json,sys
_ = {'_':time.time(),'version':20210401.3}
import win32api,win32con
from win32process import GetWindowThreadProcessId
from win32gui import \
    GetClassName,GetWindowText,GetWindowRect,\
    ClientToScreen,ScreenToClient,SendMessage,\
    GetDesktopWindow,EnumWindows,IsWindowVisible,\
    WindowFromPoint,GetCursorPos,ChildWindowFromPointEx,\
    GetWindowPlacement,ShowWindow,SetForegroundWindow,\
    PostMessage,EnumChildWindows,IsWindowEnabled

sys_import = __import__
flag_py2 = sys.version_info.major==2
sys_reload = __builtins__.reload if flag_py2 else sys_import('importlib').reload
refresh = lambda:sys_reload(sys_import(__name__))

def tryx(l,eat=True,dump=True):
    try: return l()
    except Exception as ex:
        if dump: print(ex)
        if not eat: return ex
# h=>tryx(GetClassName(h),dump=False)
cls_name = lambda h:tryx(lambda:GetClassName(h),dump=False)
win_text = lambda h:tryx(lambda:GetWindowText(h))
win_rect = lambda h:tryx(lambda:GetWindowRect(h))
#clt_rect = lambda h:tryx(lambda:GetClientRect(h))
client2screen=lambda h,p:tryx(lambda:ClientToScreen(h,p))
screen2client=lambda h,p:tryx(lambda:ScreenToClient(h,p))
htc = lambda h:(h,win_text(h),cls_name(h))
tpid = lambda h:tryx(lambda:tuple(GetWindowThreadProcessId(h)))
def win_text_set(h,t):
    tryx(lambda:SendMessage(h, win32con.WM_SETTEXT, None, str(t)))
    return myself

psub = lambda p1,p2:(p1[0]-p2[0],p1[1]-p2[1])
padd = lambda p1,p2:(p1[0]+p2[0],p1[1]+p2[1])

def sleep(t):
    time.sleep(t)
    return myself

from ctypes import windll,wintypes
# fix for main-window (who might have a win-theme-border)
def win_rect_fix(h):
    if not h: h = GetDesktopWindow()
    rect = wintypes.RECT()
    DWMWA_EXTENDED_FRAME_BOUNDS = 9
    # DwmGetWindowAttribute(h,&rect)
    windll.dwmapi.DwmGetWindowAttribute(wintypes.HWND(h),
      wintypes.DWORD(DWMWA_EXTENDED_FRAME_BOUNDS),
      ctypes.byref(rect),
      ctypes.sizeof(rect))
    _l,_t,_r,_b = (rect.left,rect.top,rect.right,rect.bottom)
    return (_l,_t,_r,_b) if _l or _t or _r or _b else win_rect(h)

rh_root = lambda h:windll.user32.GetAncestor(h,win32con.GA_ROOT)
rhtc = lambda h:htc(rh_root(h))

# rh_rootowner = lambda h:windll.user32.GetAncestor(h,win32con.GA_ROOTOWNER)
# Out: [(hdl,txt,cls,tid,pid,rh),...]
# def main_windows(reverse=True,visible=True):
#     rt = []
#     EnumWindows(lambda _h,_p:_p.append(
#         htc(_h)+tpid(_h)+(rh_rootowner(_h),)
#         ) if visible==None or visible==IsWindowVisible(_h) else None, rt)
#     if reverse: rt.reverse()
#     return rt

# pos@screen => pos@h
hp2p = lambda h,p:psub(p,win_rect_fix(h))

#### pos@screen => hwnd-of-ctrl
p2htc = lambda p=None:tryx(lambda:htc(WindowFromPoint(p or GetCursorPos())))

#### pos@win => hdl (shallow)
wp2h0 = lambda h,p,f=win32con.CWP_SKIPINVISIBLE:tryx(
    lambda:ChildWindowFromPointEx(h,p,f))

def wp2h1(h,p):
    a = win_find(h,x=p[0],y=p[1])
    if len(a)>0: return a[-1][0]
    return 0

#### win.pos => hdl (deep)
# WARN: wrong when minimized
def wp2htc(ph,p):
    # return htc(wp2h1(ph,p))
    rt = ph
    _pp = p
    _rect_ph = win_rect_fix(ph)
    while rt:
        _p = screen2client(rt,p)
        _pp = padd(_p,_rect_ph)
        _h = wp2h0(rt,_pp)
        #print('dbg.wp2htc',rt,p,_p,'pp',_pp,_rect_ph,_h)
        if not _h or _h==rt: break
        rt = _h
    if not rt:
        rt = wp2h1(ph,p) # backup plan (not yet 100% correct)
        print('dbg.wp2htc planb',htc(rt))
    return htc(rt)+_pp

#flags, state, ptMin, ptMax, rect =
win_state=lambda h:tryx(lambda:GetWindowPlacement(h or GetDesktopWindow()))

def win_change(h,fore=False,mx=None,mn=None,nm=None,rect=False,sleep=0.2):
  if mn==True: ShowWindow(h,win32con.SW_SHOWMINIMIZED)
  if mx==True: ShowWindow(h,win32con.SW_SHOWMAXIMIZED)
  if nm==True: ShowWindow(h,win32con.SW_SHOWNORMAL)
  if fore==True: tryx(lambda:SetForegroundWindow(h))
  time.sleep(sleep)
  return win_rect_fix(h)

def win_close(h):
    tryx(lambda:PostMessage(h, win32con.WM_CLOSE,0,0))
    return myself

def win_focus(h, sleep=0.02):
    SendMessage(h, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
    #time.sleep(sleep)
    return myself

def win_key_x(h,x,sleep_dn=0.02,sleep_up=0):
    print(x)#debug
    PostMessage(h, win32con.WM_KEYDOWN, x, 0)
    if sleep_up>0: time.sleep(sleep_up)
    SendMessage(h, win32con.WM_KEYUP, x, 0)
    if sleep_dn>0: time.sleep(sleep_up)
    return myself

def win_key_c(h,c,sleep=0.02):
    win_key_x(h,ord(c),sleep_up=sleep)
    return myself

def win_input_x(h,x,z=0,sleep=0.02):
    SendMessage(h, win32con.WM_CHAR,x,z)
    return myself
    
def win_input_c(h,u,sleep=0.02):
    return win_input_x(h,ord(u),sleep)

def ctrl_key(win,key=86,xkey=17):
    import win32api
    win32api.keybd_event(xkey, 0, 0, 0) #ctrl(17)
    time.sleep(0.5)
    SendMessage(win, win32con.WM_KEYDOWN, key, 0)
    win32api.keybd_event(xkey, 0, win32con.KEYEVENTF_KEYUP, 0)

# def win_event(eventType, msg):#PYQT里的函数，固定的
#     mess=  ctypes.wintypes.MSG.from_address(msg.__int__())
#     if mess.message==0x004A:
#         PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)
#         pCDS = ctypes.cast(mess.lParam, PCOPYDATASTRUCT)
#         str=ctypes.string_at(pCDS.contents.lpData)
#         print(str.decode('utf-8'))
#     return False, 0

#import ctypes
#from ctypes.wintypes import MSG    #引入ctypes的包，实现调用windows的API
#import win32gui,win32con
# TODO https://github.com/NT5/pyhelper/blob/1e229792a9057e2dfad5810094fee755194f4066/_old/beta%20concep/res/osu_np.py
#https://github.com/scsnake/miniPACS/blob/1de912a6109c0e572e9c17305f75f4dad07fd02a/win32func.py
# import array,struct
# class COPYDATASTRUCT(ctypes.Structure):
#     _fields_ = [
#         ('dwData', ctypes.wintypes.LPARAM),
#         ('cbData', ctypes.wintypes.DWORD),
#         ('lpData', ctypes.c_wchar_p)
#     ]
# PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)
# def win_send(hwnd, str, dwData=0):
#     cds = COPYDATASTRUCT()
#     cds.dwData = dwData
#     cds.cbData = ctypes.sizeof(ctypes.create_unicode_buffer(str))
#     cds.lpData = ctypes.c_wchar_p(str)

#     return ctypes.windll.user32.SendMessageW(hwnd, win32con.WM_COPYDATA, 0, ctypes.byref(cds))    
#     # int_buffer = array.array("L", [0])
#     # char_buffer = array.array('b', b"abcdefg")
#     # int_buffer_address = int_buffer.buffer_info()[0]
#     # #char_buffer = array.array('B',("12341234").encode('utf-8'))
#     # char_buffer_address, char_buffer_size = char_buffer.buffer_info()
#     # #copy_struct = struct.pack("PLP", 1, char_buffer_size, char_buffer_address)
#     # copy_struct = struct.pack("PLP", int_buffer_address, char_buffer_size, char_buffer_address)
#     # SendMessage(h, win32con.WM_COPYDATA, None, copy_struct)
#     # return copy_struct
 
# click pos@ctrl
def win_click_ctrl(h, l_or_r, p):
    _long =win32api.MAKELONG(p[0],p[1])
    _wm_dn = win32con.WM_LBUTTONDOWN if l_or_r==1 else win32con.WM_RBUTTONDOWN
    _wm_up = win32con.WM_LBUTTONUP if l_or_r==1 else win32con.WM_RBUTTONUP
    _mk = win32con.MK_LBUTTON if l_or_r==1 else win32con.MK_RBUTTON
    PostMessage(h,win32con.WM_MOVE,0,_long) # important, move little
    PostMessage(h, _wm_dn, _mk, _long)
    PostMessage(h, _wm_up, _mk, _long) # no SendMessage
    return myself

# click pos@win
def win_click(ph,l_or_r,pos_at_win):
    h,t,c,px,py = wp2htc(ph,pos_at_win)
    print('win_click',h,t,c,ph,pos_at_win)
    pos_at_screen = padd(pos_at_win,win_rect_fix(ph))
    pos_at_ph = hp2p(h,pos_at_screen)
    # print(ph,pos_at_win,'=>',h,pos_at_ph)
    return win_click_ctrl(h,l_or_r,pos_at_ph)

def rgb(pixel): return pixel & 0x0000ff, (pixel & 0x00ff00) >> 8, pixel >> 16

def probe_color(pos, h=0):
    if h==0:
        hdc = windll.user32.GetDC(0)
        pixel = windll.gdi32.GetPixel(hdc, pos[0], pos[1])
    else:
        h,t,c,px,py = wp2htc(h,pos)
        hdc = windll.user32.GetDC(h)
        pixel = windll.gdi32.GetPixel(hdc, px, py)
    return rgb(pixel) + (pixel,)
    
#def get_color(p):
#    hdc = windll.user32.GetDC(0)
#    pixel = windll.gdi32.GetPixel(hdc, p[0], p[1])  # 提取RGB值
#    return rgb(pixel) + (pixel,)

#def get_color_win(ph, pos_at_win):
#    h,t,c,px,py = wp2htc(ph,pos_at_win)
#    hdc = windll.user32.GetDC(h)
#    pixel = windll.gdi32.GetPixel(hdc, px, py)  # 提取RGB值
#    return rgb(pixel) + (pixel,)

def win_find(ph=None,pid=None,ha=None,visible=None,enable=None,
             cls=None,clsa=None,txt=None,x=None,y=None):
    if ph: tid,pid = tpid(ph)
    elif ph==0:
        #print('WARN finding root ph=0')
        ''
    elif not pid:
        print('ERR: win_find() needs ph or pid')
        return None
    if ph!=None:
        pha = [ph]
    else:# using pid to filter
        pha = []
        def _filter0(_h,_p):
            #if not IsWindowVisible(_h): return
            _tid,_pid = tpid(_h)
            if pid == _pid:
                # print('tmp',pid,_pid,_h,cls_name(_h),win_text(_h))
                _p.append(_h)
        EnumChildWindows(0,_filter0,pha)
        pha.reverse()
    # print('pha',pha,'pid',pid)
    rt=[]
    for _ph in pha:
        ph_x=0
        ph_y=0
        if x and y:
            if _ph>0: # not desktop
                _rect = win_rect_fix(_ph)
                print('dbg.win_find():_rect,_ph',_rect,_ph)
                ph_x,ph_y,ph_r,ph_b = _rect
        def _filter(_h,p):
          flag_append = True
          _txt=win_text(_h)
          _cls=cls_name(_h)
          _tid,_pid = tpid(_h)
          if ha and _h not in ha: flag_append = False
          _visible = IsWindowVisible(_h)
          if None!=visible and visible!=_visible: flag_append = False
          _enable = IsWindowEnabled(_h)
          if None!=enable and enable!=_enable: flag_append = False
          if pid and pid!=_pid: flag_append = False
          if flag_append:
              if clsa and (_cls not in clsa):
                  flag_append = False
          if cls and cls!=_cls: flag_append = False
          if txt!=None and txt!=_txt: flag_append = False
          # todo: what if using win_rect_fix??
          # todo: any improvement here...
          rect = win_rect(_h)
          ww = rect[2]-rect[0]
          hh = rect[3]-rect[1]
          if flag_append and x and y:
              if _h==0: # desktop skip
                  flag_append = True
              else:
                  xx = x + ph_x
                  yy = y + ph_y
                  if not (xx>=rect[0] and xx<=rect[2] and yy>=rect[1] and yy<=rect[3]):
                      # print('X',_h,rect,(xx,x,ph_x),(yy,y,ph_y),_txt,_cls)
                      flag_append = False
                  # else: print('=>',_h,rect,xx,yy,_txt,_cls)
          if flag_append:
              p.append((_h,_txt,_cls,_pid,_visible,_enable,_ph,rect,(ww,hh)))
          #elif _visible: print('?',_h,_txt,_cls,clsa)
        EnumChildWindows(_ph,_filter,rt)
    return rt

def mon():
    prev_pos = None
    while True: # quick spy ;)
        time.sleep(1)
        screen_pos = win32api.GetCursorPos()

        # skip if no move
        if screen_pos == prev_pos: continue

        #_hdl,_txt,_cls = p2htc()
        _hdl,_txt,_cls = p2htc(screen_pos)
        tid,pid = tpid(_hdl)

        ph,p_txt,p_cls = rhtc(_hdl)
        ptid,ppid = tpid(ph)

        rect = win_rect_fix(ph)
        
        pos_ctrl_at_win = hp2p(ph,screen_pos)

        cch2,cch2_txt,cch2_cls,px,py = wp2htc(ph,pos_ctrl_at_win) 

        print('\nscreen',screen_pos,_hdl,_cls,_txt,pid,probe_color(screen_pos),
                '\n win',rect,ph,p_cls,p_txt,ppid,
                '\n ctrl@win',pos_ctrl_at_win,cch2,cch2_cls,cch2_txt,
                '\n pos@ctrl',(px,py), probe_color(pos_ctrl_at_win,ph))
        prev_pos = screen_pos

# wins = lambda ph=[0],ha=None,cls=None,txt=None,full=False,visible=True,enable=True:[ v if full else v[0] for _h in ph for v in win_find(ph=_h,ha=ha,cls=cls,txt=txt)]
# wins = lambda ph=[0],ha=None,cls=None,clsa=None,txt=None,full=False,visible=True,enable=False:[ v if full else v[0] for _cls in (clsa if clsa else [cls]) for _h in ph for v in win_find(ph=_h,ha=ha,cls=_cls,txt=txt)]
wins = lambda ph=[0],ha=None,cls=None,clsa=None,txt=None,full=False,visible=None,enable=None:[ v if full else v[0] for _h in ph for v in win_find(ph=_h,ha=ha,clsa=clsa if clsa else [cls] if cls else None,txt=txt)]

json_dumps = lambda o,format=True,indent=None:json.dumps(o,ensure_ascii=False,indent=indent)
list_dumps = lambda l:len([print(v) for v in l])

def input(h, s, sleep=0.02, focus=True, clear=False):
    if focus:
        win_focus(h)
        time.sleep(sleep)
    if clear:
        win_text_set(h, '')
    for c in s: win_input_c(h,c,sleep)
    return myself

def paste(h, txt, focus=True, restore=False):
    import win32con
    import win32clipboard as cp

    if focus:
        win_focus(h)

    # todo: backup+restore clipboard when enter/exit
    cp.OpenClipboard()
    if restore:
        _old= cp.GetClipboardData()
    cp.EmptyClipboard()
    cp.SetClipboardData(win32con.CF_UNICODETEXT, txt)
    #if type='img': cp.SetClipboardData(win32con.CF_BITMAP, data)
    #cp.GetClipboardData()
    #rst = cp.GetClipboardData(win32con.CF_UNICODETEXT)  # 输出：132465
    #print(rst)
    #result1 = cp.GetClipboardData(win32con.CF_TEXT)  # 输出：b'`O}Y\x00'
    #print(result, result1)
    cp.CloseClipboard()  # 关闭剪贴板
    #tryx(lambda:PostMessage(h,win32con.WM_PASTE,0,0)) #faile
    ctrl_key(h,key=86)#ctrl-v(86)
    if restore:
        cp.EmptyClipboard()
        cp.SetClipboardData(win32con.CF_UNICODETEXT, _old)
    return myself
    
########################################## chain pattern
class bot:
    def __init__(self,h=None,ha=None,debug=True,clsa=None):
        self.h = h if h else 0
        self.ha = ha
        self.clsa = clsa
        self.debug = debug
    # def _ha(self): return self.ha if self.ha else [self.h]
    def _ha(self):
        if self.ha:
            return self.ha
        elif self.clsa:
            _ha = wins(clsa=self.clsa)
            # print('clsa',self.clsa, _ha)
            return _ha
        else:
            return [self.h]
    # for quick dump
    def __repr__(self):
        _ha = self._ha()
        rt = []
        for h in _ha:
          _txt=win_text(h)
          _cls=cls_name(h) if h>0 else None
          rt.append((h,_cls,_txt))
        return json.dumps(rt,ensure_ascii=False)
    def __getitem__(self,k):# []
        print('[]/__getitem__',k)
    def fore(self,mx=False,sleep=0.2): # todo 
        for _h in self._ha(): win_change(_h,fore=True,mx=mx)
        time.sleep(sleep)
        return self

    def click(self, l_or_r,p,idx=0,clsa=None,cls=None,txt=None,debug=True,sleep=0.2):
        _wins = self._ha()
        if clsa or cls or txt:
            _winsx = wins(ph=_wins,clsa=clsa,cls=cls,txt=txt)
            if len(_winsx)>0: _wins = _winsx
        print('click _wins',_wins)
        for h in _wins:
            win_click(h,l_or_r,p)
            time.sleep(sleep)
            # break # todo only 1 / ==idx
        return self
    def sleep(self, t): time.sleep(t); return self
    def input(self,s,cls=None,txt=None,idx=0,sleep=0.2):
        _wins = self._ha()
        if cls or txt:
            _winsx = wins(ph=_wins,cls=cls,txt=txt)
            if len(_winsx)>0: _wins = _winsx
        print('input _wins',_wins)
        for h in _wins:
            input(h,s,sleep)
            #win_focus(h)
            #for c in s: win_key_c(h,c,sleep=sleep)
            # break # todo only 1 / ==idx
        return self
    def keys(self,s,cls=None,txt=None,idx=0,sleep=0.2):
        _wins = self._ha()
        if cls or txt:
            _winsx = wins(ph=_wins,cls=cls,txt=txt)
            if len(_winsx)>0: _wins = _winsx
        print('input _wins',_wins)
        for h in _wins:
            #key(h,s,sleep)
            win_focus(h)
            for c in s: win_key_c(h,c,sleep=sleep)
            # break # todo only 1 / ==idx
        return self

def test(req=None, ph=0, debug=False,cls=None,txt=None):

  def _chk(h):
    try:
      _cls=cls_name(h)
      if _cls=='TMainForm':win_text_set(h,'fuyi')
      if _cls=='#32770':win_text_set(h,'zhushou')
      if _cls=='Afx:400000:b:10003:6:7fdd13a7':win_text_set(h,'tdx')
      _txt=win_text(h)
      tid,pid = tpid(h)
      act = None
      # if _cls=='ConsoleWindowClass': act = win_close(h)
      # if _cls=='TaskManagerWindow': act = win_close(h)
      if _cls=='mininews': act = win_close(h)
      if _cls=='TXGuiFoundation' and _txt=='腾讯网迷你版':
        act = win_close(h)
      #if _cls=='#32770' and _txt=='多帐户登录设置'
      if _txt=='多帐户登录设置' or _txt=='多帐户批量快速登录':
        act = win_close(h)
      rt = (h, hex(h), _txt, _cls, act, IsWindowVisible(h),pid)
      if debug:
        print(rt)
      return rt
    except Exception as ex:
      print(ex)

  w_a = win_find(ph,cls=cls,txt=txt)
  rt_a = [ _chk(v[0]) for v in w_a ]
  return rt_a

bots = lambda ph=[0],ha=None,cls=None,clsa=None,txt=None:bot(
    ha=wins(ph,ha,cls,txt) if not clsa else None,clsa=clsa)

def ensure_win_mx(h,sleep_else=0,sleep_mx=1):
    flags, state, ptMin, ptMax, rect = rt = win_state(h)
    if state==win32con.SW_SHOWMINIMIZED:
        win_change(h,mx=True)
        time.sleep(sleep_mx)
    else:
        time.sleep(sleep_else)
    return rt

### ext quick tools
def wx_send(who,txt,mode='paste'):
    w=tryx(lambda:win_find(0,cls='ChatWnd',txt=who)[0][0])
    if w:
        ensure_win_mx(w)
        paste(w,txt)
        # if mode=='paste':
        #     paste(w,txt)
        # else:
        #     input(w, txt)#, focus=False)
        SendMessage(w, win32con.WM_KEYDOWN, win32con.VK_RETURN,0)
    else:
        # todo dbl-click the ico and input $who at search bar...
        print('not found ChatWnd @',who)
    return myself

def qq_send(who,txt):
    w=tryx(lambda:win_find(0,cls='TXGuiFoundation',txt=who)[0][0])
    if w:
        input(w, txt)
        SendMessage(w, win32con.WM_KEYDOWN, win32con.VK_RETURN,0)
    else:
        # todo dbl-click the ico and input $who at search bar...
        print('not found qq @',who)
    return myself

class probe:
    def __init__(self,ev): self._ev=ev
    def __getattr__(self,k): return self._ev(k)

myself = probe(lambda k:eval(k))
#print(myself)

if __name__ == '__main__':
    test()
    mon()
