import dis
import imp
import sys
sys.path.append("../..")
sys.path.append("../")
from MicroRTS_NB import PhysicalGameState
from MicroRTS_NB import UnitTypeTable
from MicroRTS_NB import GameState
from MicroRTS_NB import Unit
from MicroRTS_NB import Player
import time

from ai.abstraction.AbstractionLayerAI import AbstractionLayerAI

class CombatRush(AbstractionLayerAI):
    def __init__(self, pgs : PhysicalGameState, utt,combatType :str  ):
        super().__init__(pgs)
        self._utypeWorker = utt.getUnitTypeString("Worker")
        self._utypeBarrack = utt.getUnitTypeString("Barracks")
        self._utypeCombat = utt.getUnitTypeString(combatType)
        self._t0=0
        self._t1=0
        self._t2=0
        self._t3=0
        self._t4=0
    def setAttack(self, u : Unit, enemies : list[Unit] )  :
        enemy = self.getClosest(u,enemies)
        if enemy != None:
            self.attack(u, enemy)
                

    def setBuild(self,u :Unit, p :Player, gs :GameState):
         reservedPositions = []
         self.buildIfNotAlreadyBuilding(u,self._utypeBarrack,u.getX(),u.getY(),reservedPositions,p,gs);
                
    def getClosest(self, u: Unit, l :list[Unit]):
        target = None
        distance =-1
        for u2 in l:
            dx = (u.getX()-u2.getX())**2
            dy = (u.getY()-u2.getY())**2
            d = (dy+dx)**0.5
            if d<distance or target ==None:
                distance = d
                target = u2
        return target

    def setTrain(self,u,utype):
        self.train(u, utype)
        

    def setHarvest(self,u :Unit,bases :list[Unit],resources :list[Unit]):
        target =  self.getClosest(u,resources)
        base =  self.getClosest(u,bases)
        self.harvest(u, target, base)

    def getActions(self,gs : GameState,player : int):
        
        pgs = gs.getPhysicalGameState()
        p = gs.getPlayer(player)
        units = {"Base":[],"Barracks":[],"Worker":[],self._utypeCombat.getName():[],
                 "Resource":[],"Enemies":[]}
       
        
        
     
        inicio = time.time()
        for u in pgs.getUnits(player).values():
            name = u.getType().getName()
            if name == self._utypeCombat.getName()  and gs.getActionAssignment(u)==None:
                units[self._utypeCombat.getName()].append(u)
            else:
                units[name].append(u)
        for u in pgs.getUnits(1 - player).values():
                units["Enemies"].append(u)
        for u in pgs.getUnits(-1).values():
                units["Resource"].append(u)     
        


        
        fim = time.time()
        self._t0+=fim - inicio 
        inicio = time.time()
        for u in units["Barracks"]:
            self.setTrain(u,self._utypeCombat)
        fim = time.time()     
        self._t1+=fim - inicio 
        inicio = time.time()
        
        for u in units[self._utypeCombat.getName()]:
            self.setAttack(u,units["Enemies"])
        fim = time.time()     
        self._t2+=fim - inicio 
        inicio = time.time()
  
        for u in units["Base"]:
            if len(units["Worker"])<1 and gs.getActionAssignment(u)==None:
                self.setTrain(u,self._utypeWorker)
      
        for u in units["Worker"]:
            if gs.getActionAssignment(u)!=None:
                continue
            elif len(units["Barracks"])<1 and p.getResources()>=5:
                self.setBuild(u,p,gs)
            elif len(units["Base"])>0 and len(units["Resource"])>0:
                self.setHarvest(u,units["Base"],units["Resource"])
            else:
                self.setAttack(u,units["Enemies"])
        
        fim = time.time()     
        self._t3+=fim - inicio 
        inicio = time.time()
        
        p0=self.translateActions(player,gs)
        fim = time.time()     
        self._t4+=fim - inicio 
 
        return p0
        
        
   