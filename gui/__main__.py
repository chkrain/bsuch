import sys
from pysca import app
from pysca.device import PYPLC
from concrete6 import concrete6
import pygui.navbar as navbar

def main():
    import argparse
    args = argparse.ArgumentParser(sys.argv)
    args.add_argument('--device', action='store', type=str, default='192.168.4.1', help='IP address of the device')
    args.add_argument('--simulator', action='store_true', default=False, help='Same as --device 127.0.0.1')
    ns = args.parse_known_args()[0]
    if ns.simulator:
        ns.device = '127.0.0.1'
        import subprocess
        logic = subprocess.Popen(["python3", "src/krax.py"])
    
    dev = PYPLC(ns.device)
    app.devices['PLC'] = dev
    
    Home = app.window('ui/Home.ui')
    Extensions = app.window('ui/Extensions.ui')
    app.animate(concrete6.instance)
    # с использованием navbar
    navbar.append(Home)
    navbar.tools(Extensions)
    navbar.instance.show( )
    concrete6.setContainerPanels([Home.doserpanel_0, Home.doserpanel_1, Home.doserpanel_2, Home.doserpanel_3, Home.doserpanel_4, Home.doserpanel_5])
    concrete6.reload( )
    concrete6.setMainWindow(navbar.instance)
    # или 
    # Home.show()               
    
    dev.start(100)
    app.start( ctx = globals() )
    dev.stop( )

    if ns.simulator:
        logic.terminate( )
        pass
    concrete6.save()

if __name__=='__main__':
    main( )
    