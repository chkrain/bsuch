from pyplc.platform import plc, plc as io
from pyplc.utils.misc import BLINK
from pyplc.utils.latch import RS
from pyplc.utils.trig import RTRIG
from concrete import Factory,Motor, Mixer, MSGate as Gate,Lock,Transport,Weight,Container,Dosator,Manager,Readiness,Loaded
from concrete.vibrator import Vibrator,UnloadHelper
from concrete.imitation import iMOTOR,iGATE,iVALVE,iWEIGHT,IRotation
from sys import platform
from pyplc.utils.misc import TOF
from pyplc.pou import POU 
from collections import namedtuple

if platform == 'vscode':
    PLC = namedtuple('PLC', ("WATER_M_1", "ADDITION_M_1", "CEMENT_M_1", "FILLERS_M_1", "MIXER_I_1","DWATER_OPEN_1", "DADDITIONS_OPEN_1", "DCEMENT_OPEN_1","GWATER_OPEN_1", "GADDITIONS_OPEN_1", "GADDITIONS_OPEN_2", "GCEMENT_OPEN_1","FEEDER_OPEN_1", "FEEDER_OPEN_2","AERATOR_ON_1", "AERATOR_ON_2","FVIBRATOR_ON_1", "FVIBRATOR_ON_2","SVIBRATOR_ON_1", "SVIBRATOR_ON_2","CVIBRATOR_ON_1","PVIBRATOR_ON_1","MIXER_ON_1", "MIXER_OFF_1","APUMP_ON_1", "APUMP_ON_2","MIXER_OPEN_1","CONVEYOR_ON_1", "TCONVEYOR_ON_1","CALL_ON_1","WPUMP_ON_1","AUGER_ON_1", "AUGER_ON_2","GFEEDER_OPENED_1", "GFEEDER_OPENED_2","DWATER_CLOSED_1", "DADDITIONS_CLOSED_1", "DCEMENT_CLOSED_1","CONVEYOR_ISON_1", "TCONVEYOR_ISON_1","GWATER_CLOSED_1", "GADDITIONS_CLOSED_1", "GADDITIONS_CLOSED_2", "GCEMENT_CLOSED_1","MIXER_ISON_1","MIXER_CLOSED_1", "MIXER_OPENED_1","MIN_1", "MAX_1", "MIN_2", "MAX_2","AUGER_ISON_1", "AUGER_ISON_2","APUMP_ISON_1", "APUMP_ISON_2","BELT_1", "BELT_2","WPUMP_ISON_1","POWERFAIL", "ACCIDENT"))
    io = PLC()

factory_1 = Factory()

cement_m_1 = Weight(raw=io.CEMENT_M_1, mmax=1500)
auger_1 = Container(m = cement_m_1.get_m, out = io.AUGER_ON_1, lock=Lock(key=~io.DCEMENT_CLOSED_1),closed=~io.AUGER_ISON_1,max_sp=1000)
auger_2 = Container(m = cement_m_1.get_m, out = io.AUGER_ON_2, lock=Lock(key=~io.DCEMENT_CLOSED_1),closed=~io.AUGER_ISON_2,max_sp=1000)
dcement_1 = Dosator(m = cement_m_1.get_m, closed = io.DCEMENT_CLOSED_1, out = io.DCEMENT_OPEN_1, lock=Lock(key=lambda: io.AUGER_ON_1 or io.AUGER_ON_2), containers=(auger_1, auger_2, ))
aerator_1 = BLINK(enable=io.AUGER_ON_1,q=io.AERATOR_ON_1)
aerator_2 = BLINK(enable=io.AUGER_ON_2,q=io.AERATOR_ON_2)    
dc_vibrator_1 = UnloadHelper(q=io.PVIBRATOR_ON_1, dosator=dcement_1,weight=cement_m_1)

class WPUMP(POU):
    force = POU.var(False)
    q = POU.output(False)
    
    def __init__(self, auto, q: bool, *, id: str = None, parent: POU = None):
        super().__init__(id, parent)
        self.q = q
        self.delay = TOF(clk=auto, pt=2000)
    
    def __call__(self):
        with self:
            self.q = self.delay() or self.force

water_m_1 = Weight(raw=io.WATER_M_1, mmax=500)
water_1 = Container(m = water_m_1.get_m, out = io.GWATER_OPEN_1, lock=Lock(key=~io.DWATER_CLOSED_1),closed=io.GWATER_CLOSED_1,max_sp=500)
wpump_1 = WPUMP(auto=lambda: io.GWATER_OPEN_1, q=io.WPUMP_ON_1)
dwater_1 = Dosator(m = water_m_1.get_m, closed = io.DWATER_CLOSED_1, out = io.DWATER_OPEN_1, lock=Lock(False), containers=(water_1,))

additions_m_1 = Weight(raw=io.ADDITION_M_1, mmax=50)
addition_1 = Container(m = additions_m_1.get_m, out = io.GADDITIONS_OPEN_1, lock=Lock(key=lambda: not io.DADDITIONS_CLOSED_1 or not io.GADDITIONS_CLOSED_2),closed=io.GADDITIONS_CLOSED_1,max_sp=50)
addition_2 = Container(m = additions_m_1.get_m, out = io.GADDITIONS_OPEN_2, lock=Lock(key=lambda: not io.DADDITIONS_CLOSED_1 or not io.GADDITIONS_CLOSED_1),closed=io.GADDITIONS_CLOSED_2,max_sp=50)
apump_1 = WPUMP(auto=lambda: io.GADDITIONS_OPEN_1, q=io.APUMP_ON_1)
apump_2 = WPUMP(auto=lambda: io.GADDITIONS_OPEN_2, q=io.APUMP_ON_2)
dadditions_1 = Dosator(m = additions_m_1.get_m, closed = io.DADDITIONS_CLOSED_1, out = io.DADDITIONS_OPEN_1, lock=Lock(False), containers=(addition_1,addition_2))

fillers_m_1 = Weight(raw=io.FILLERS_M_1, mmax=8000)
filler_1 = Container(m = fillers_m_1.get_m, out = io.FEEDER_OPEN_1, lock=Lock(key=lambda: io.CONVEYOR_ON_1 or io.FEEDER_OPEN_2),closed=~io.FEEDER_OPEN_1,max_sp=3000)
filler_2 = Container(m = fillers_m_1.get_m, out = io.FEEDER_OPEN_2, lock=Lock(key=lambda: io.CONVEYOR_ON_1 or io.FEEDER_OPEN_1),closed=~io.FEEDER_OPEN_2,max_sp=3000)
dfillers_1 = Dosator(m = fillers_m_1.get_m, closed = ~io.CONVEYOR_ON_1, out = io.CONVEYOR_ON_1, lock=Lock(key=lambda: io.FEEDER_OPEN_1 or io.FEEDER_OPEN_2), containers=(filler_1,filler_2))

vibrator_1 = Vibrator(q=io.FVIBRATOR_ON_1,containers=(io.FEEDER_OPEN_1,io.FEEDER_OPEN_2),weight=fillers_m_1)
vibrator_2 = Vibrator(q=io.FVIBRATOR_ON_2,containers=(io.FEEDER_OPEN_2,io.FEEDER_OPEN_1),weight=fillers_m_1)

motor_1 = Motor(ison=io.MIXER_ISON_1, bell=io.CALL_ON_1,on=io.MIXER_ON_1, off=io.MIXER_OFF_1)
tconveyor_1 = Transport(ison=io.TCONVEYOR_ISON_1,power=io.TCONVEYOR_ON_1,out=None)
gate_1 = Gate(closed = io.MIXER_CLOSED_1,opened=io.MIXER_OPENED_1, open=io.MIXER_OPEN_1)
mixer_1 = Mixer(gate=gate_1,motor=motor_1,flows=[ x.q for x in [auger_1,auger_2,water_1,addition_1,addition_2]] + [x.q for x in [filler_1, filler_2]])

ready_1 = Readiness([dcement_1,dwater_1,dadditions_1,dfillers_1])
loaded_1 = Loaded([dcement_1,dwater_1,dadditions_1])

def loading():
  dfillers_1.unload = True
  dadditions_1.unload = True
  while not dfillers_1.unload: yield 
  dcement_1.unload = True
  dwater_1.unload = True

manager_1 = Manager( mixer=mixer_1,collected=ready_1,loaded = loaded_1,dosators=(dcement_1,dwater_1,dadditions_1,dfillers_1),loadOrder=loading )

factory_1.on_mode = [ x.switch_mode for x in [dcement_1,dwater_1,dadditions_1,dfillers_1] ]
factory_1.on_emergency = [ x.emergency for x in [dcement_1,dwater_1,dadditions_1,dfillers_1,mixer_1,manager_1] ]
factory_1.emergency = io.ACCIDENT
factory_1.powerfail = io.POWERFAIL

instances = (factory_1, motor_1,gate_1,tconveyor_1,
            cement_m_1,auger_1,auger_2,dcement_1,
            water_m_1,water_1,dwater_1,wpump_1,
            additions_m_1,addition_1,addition_2,dadditions_1,apump_1,apump_2,
            fillers_m_1,filler_1,filler_2,dfillers_1,
            mixer_1,
            ready_1,loaded_1,manager_1,
            vibrator_1,vibrator_2,dc_vibrator_1,aerator_1,aerator_2,
            RTRIG(clk=lambda: io.CONVEYOR_ON_1, q=tconveyor_1.set_auto),
            )

if platform=='linux':
  imotor_1 = iMOTOR(simple=False,on = io.MIXER_ON_1,ison=io.MIXER_ISON_1, off=io.MIXER_OFF_1)
  igate_1 = iGATE(open=io.MIXER_OPEN_1,closed=io.MIXER_CLOSED_1,opened=io.MIXER_OPENED_1,simple=True, close=~io.MIXER_OPEN_1)
  iauger_1 = iMOTOR(simple=True,on = io.AUGER_ON_1,ison=io.AUGER_ISON_1)
  iauger_2 = iMOTOR(simple=True,on = io.AUGER_ON_2,ison=io.AUGER_ISON_2)
  iwpump_1 = iMOTOR(simple=True,on = io.WPUMP_ON_1,ison=io.WPUMP_ISON_1)
  iapump_1 = iMOTOR(simple=True,on = io.APUMP_ON_1,ison=io.APUMP_ISON_1)
  iapump_2 = iMOTOR(simple=True,on = io.APUMP_ON_2,ison=io.APUMP_ISON_2)
  iconveyor_1 = iMOTOR(simple=True,on = io.CONVEYOR_ON_1,ison=io.CONVEYOR_ISON_1)
  itconveyor_1 = iMOTOR(simple=True,on = io.TCONVEYOR_ON_1,ison=io.TCONVEYOR_ISON_1)
  idcement_1 = iVALVE(open=io.DCEMENT_OPEN_1,closed=io.DCEMENT_CLOSED_1)
  idwater_1 = iVALVE(open=io.DWATER_OPEN_1,closed=io.DWATER_CLOSED_1)
  igwater_1 = iVALVE(open=io.GWATER_OPEN_1, closed=io.GWATER_CLOSED_1)
  igadditions_1 = iVALVE(open=io.GADDITIONS_OPEN_1, closed=io.GADDITIONS_CLOSED_1)
  igadditions_2 = iVALVE(open=io.GADDITIONS_OPEN_2, closed=io.GADDITIONS_CLOSED_2)
  idadditions_1 = iVALVE(open=io.DADDITIONS_OPEN_1,closed=io.DADDITIONS_CLOSED_1)
  ifeeder_1 = iMOTOR(simple=True,on = io.FEEDER_OPEN_1,ison=io.GFEEDER_OPENED_1)
  ifeeder_2 = iMOTOR(simple=True,on = io.FEEDER_OPEN_2,ison=io.GFEEDER_OPENED_2)
  ibelt_1 = IRotation( q = io.CONVEYOR_ON_1, rot = io.BELT_1 )
  ibelt_2 = IRotation( q = io.TCONVEYOR_ON_1, rot = io.BELT_2 )
  
  icement_m_1 = iWEIGHT(speed=100,loading=lambda: io.AUGER_ON_1 or io.AUGER_ON_2, unloading=io.DCEMENT_OPEN_1, q = io.CEMENT_M_1)
  iwater_m_1 = iWEIGHT(speed=100,loading=lambda: io.GWATER_OPEN_1, unloading=io.DWATER_OPEN_1, q = io.WATER_M_1)
  iadditions_m_1 = iWEIGHT(speed=100,loading=lambda: io.GADDITIONS_OPEN_1 or io.GADDITIONS_OPEN_2, unloading=io.DADDITIONS_OPEN_1, q = io.ADDITION_M_1)
  ifillers_m_1 = iWEIGHT(speed=100,loading=lambda: io.FEEDER_OPEN_1 or io.FEEDER_OPEN_2, unloading=io.CONVEYOR_ON_1, q = io.FILLERS_M_1)
    
  instances += (imotor_1,igate_1,iauger_1,iauger_2,iwpump_1,iapump_1,iapump_2,iconveyor_1,itconveyor_1,idcement_1,igwater_1,idwater_1,igadditions_1,igadditions_2,idadditions_1,ifeeder_1,ifeeder_2,
                icement_m_1,iwater_m_1,iadditions_m_1,ifillers_m_1, ibelt_1, ibelt_2)

if platform=='esp32':
    from board import tick
    instances+=(tick,)

# io.name = 'plc'
plc.run( instances=instances, ctx=globals() )
