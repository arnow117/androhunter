"""
DexRouter from arnow117

Source all target pattern, generate possible attack chain

Refer to SCRIPTS.TXT for more information.
"""

from java.lang import Runnable, Thread
from com.pnfsoftware.jeb.client.api import IScript, IGraphicalClientContext, IconType, ButtonGroupType
from com.pnfsoftware.jeb.core.output.text import ITextDocument
from com.pnfsoftware.jeb.core import RuntimeProjectUtil
from com.pnfsoftware.jeb.core.units import IXmlUnit
from com.pnfsoftware.jeb.core.units.code import ICodeUnit, ICodeItem
from com.pnfsoftware.jeb.core.units.code.android import IApkUnit
from com.pnfsoftware.jeb.core.actions import Actions, ActionContext, ActionXrefsData, ActionOverridesData
import re
import os


class dexrouter(IScript):
    def run(self, ctx):
        #IGraphicalClientContext
        optionString = "ZipEntry;->getName/Context;->startActivity"
        searchString = ctx.displayQuestionBox('Set Term Pattern','Regex pattern to be routed for term : ', '%s'%optionString)
        ctx.executeAsync("Running DexRouter Async...", DexRouterAsync(ctx,searchString))
        print('Done')

class DexRouterAsync(Runnable):
    def __init__(self, ctx, searchString):
        self.ctx = ctx
        self.searchString = searchString

    def run(self):
        ctx = self.ctx 
        print("==========================START==========================")
            
        self.pattern = re.compile(self.searchString, re.I)
        self.result = [[]]

        if not self.pattern:
            print('Please provide a search string')
            return

        engctx = ctx.getEnginesContext()
        if not engctx:
            print('Back-end engines not initialized')
            return

        projects = engctx.getProjects()
        if not projects:
            print('There is no opened project')
            return

        prj = projects[0]
        # print('Searching "%s" ...' % searchstring)
        # self.apkUnit = RuntimeProjectUtil.findUnitsByType(prj, IXmlUnit, False)
        # for unit in self.apkUnit:
        #     # acts = unit.getActivities()
        #     # print(acts)
        #     # print(unit.getName())
        #     if "Manifest" in unit.getName():
        #         print(unit.getDocument())
        #     #     self.targetApk = unit
        #     #     break

        # return
        self.codeUnit = RuntimeProjectUtil.findUnitsByType(prj, ICodeUnit, False)
        path = prj.getName()
        self.path = os.path.join(os.path.dirname(path),os.path.basename(path)[:os.path.basename(path).index('.')]+".router")
        self.fd = open(self.path,"w+")
    
        for unit in self.codeUnit:
            classes = unit.getClasses()
            if classes and "bytecode" in unit.getName().lower():
                targetUnit = unit
                break
           
        # units = RuntimeProjectUtil.findUnitsByType(prj, IJavaSourceUnit, False)
        self.targetUnit = targetUnit
        # class->method->instruction
        # for clz in targetUnit.getClasses():
        #     if self.isTargetName(clz.getSignature(False)):
        #         for method in clz.getMethods():
        #             print("method::")
        #             for inst in method.getInstructions():
        #                 print("%s"%(inst.format(ctx)))#only get method index

        # return 
        self.resultRouteLists = [[]]
        self.routeStartIndex = []
        self.routeList = []

        self.routeCache = {}
        for m in targetUnit.getMethods():
            # self.fd.write(m.getSignature(False)+'\n')
            l = []
            if self.isTargetName(m.getSignature(False)):
                self.fd.write("Find route for : %s \n"%m.getSignature(False))
                # print("target id: %s index: %s address: %s"%(m.getItemId(),m.getIndex(),m.getAddress()))
                self.i = 1
                a = self.findXrefR(0,l,m.getItemId(),m.getAddress())
                self.fd.write("==========================RouteList: %d==========================\n"%self.i)
                for route in self.routeList:
                    self.fd.write("%s\n"%("==>".join(route)))
                # self.resultRouteLists.append(self.routeList)
                self.routeList = []
                self.i += 1 
                # break
        
        print("[+] Route file: %s"%self.path)
        self.fd.close()
    
    
    
    def getClassSupertypesR(self, l,codeClass):
        for c in codeClass.getSupertypes():
            l.append(c.getAddress())
            c = self.targetUnit.getClass(c.getAddress())
            if c and c.getSupertypes():
                self.getClassSupertypesR(l,c)
        return l

    def getImplementedInterfacesR(self, l,codeClass):
        for c in codeClass.getImplementedInterfaces():
            l.append(c.getAddress())
            c = self.targetUnit.getClass(c.getAddress())
            if c and c.getImplementedInterfaces():
                self.getClassSupertypesR(l,c)
        return l

    def addRoute(self, start, routeList):
        if start not in self.routeStartIndex:
            self.routeStartIndex.append(start)
            self.routeList.append(routeList)

    def addr2Sign(self,addr):
        return addr[:addr.index("+")]
    
    def addr2ClassName(self,addr):
        return addr[:addr.index(";")+1]

    def isTargetName(self, cn):
        return self.pattern.search(cn) is not None

    def asmResult(self,tList,sAddr,dAddr):
        if len(tList) == 0:
            tList.append(dAddr)
            tList.append(sAddr)
            return tList
        if sAddr != tList[-1]:
            tList.append(sAddr)
            return tList

    def searchXref(self,dId, dAddr):
        actCntx = ActionContext(self.targetUnit, Actions.QUERY_XREFS, dId, dAddr)
        actData = ActionXrefsData()
        if(self.targetUnit.prepareExecution(actCntx, actData)):
            try:
                bRlt = self.targetUnit.executeAction(actCntx, actData)
                if(not bRlt):
                    print('executeAction fail!')
            except Exception, e:
                print Exception, ":", e
                return []
        return actData.getAddresses()
    
    def searchOveride(self,dId, dAddr):
        actCntx = ActionContext(self.targetUnit, Actions.QUERY_OVERRIDES, dId, dAddr)
        actData = ActionOverridesData()
        if(self.targetUnit.prepareExecution(actCntx, actData)):
            try:
                bRlt = self.targetUnit.executeAction(actCntx, actData)
                if(not bRlt):
                    print('executeAction fail!')
            except Exception, e:
                print Exception, ":", e
                return []
        return actData.getAddresses()

    def searchWithCache(self,type,dId,dAddr):
        # type--0--xref, type--1--overide
        if type == 0 :
            if self.routeCache.get(dId):
                return self.routeCache.get(dId)
            else:
                #exist or []
                self.routeCache[dId] = []
                self.routeCache[dId].extend(self.searchXref(dId,dAddr))
                return self.routeCache.get(dId)
        elif type == 1 :
            if self.routeCache.get(str(dId)+'over'):
                return self.routeCache.get(str(dId)+'over')
            else:
                #exist or []
                self.routeCache[str(dId)+'over'] = []
                self.routeCache[str(dId)+'over'].extend(self.searchOveride(dId,dAddr))
                return self.routeCache.get(str(dId)+'over')
    
    def findXrefR(self, maxDeepth ,orginList, dId, dAddr, overideClassName=None):
        xrefs = self.searchWithCache(0, dId, dAddr)
    
        if maxDeepth == 40:
            # self.fd.write("maxium!!! \n")
            # self.fd.write("orginList: %s \n"%orginList)
            return None

        # select for xref result, grep the exist xref chain item, and some SDK classes
        s = set()
        for t in xrefs:
            methodAddr = self.addr2Sign(t)
            if methodAddr == dAddr:
                continue
            if methodAddr in orginList or "Ljava" in self.addr2ClassName(t) or "Landroid" in self.addr2ClassName(t):
                # return None
                continue
            if overideClassName:
                clz = self.targetUnit.getClass(self.addr2ClassName(t))
                sClasses = set()
                supers = self.getClassSupertypesR([],clz)
                impls = self.getImplementedInterfacesR([],clz)
                for s1 in supers:
                    sClasses.add(s1) 
                for s2 in impls:
                    sClasses.add(s2)            
                # print("overideClassName: %s\n sclasses: %s\n"%(overideClassName,sClasses))
                if overideClassName not in sClasses:
                    s.add(self.targetUnit.getMethod(self.addr2Sign(t)))
                # else:
                #     print("grep method: %s"%self.addr2Sign(t))
            else:
                s.add(self.targetUnit.getMethod(self.addr2Sign(t)))
        # print("grep set %s" % s)
        
        if len(list(s)) == 0:
            # find no xref, find directly override
            oMethods = self.findParentMethods(dAddr)
            # print("parent method %s" % oMethod)
            
            if len(oMethods) == 0:
                s = False
                s = self.findClousureClassXref(maxDeepth+1,orginList,dAddr,"Landroid/os/AsyncTask;") or self.findClousureClassXref(maxDeepth+1,orginList,dAddr,"Ljava/lang/Runnable;")
                if not s:
                    orginList.reverse()
                    if len(orginList) == 0:
                        return None
                    classes = self.getClassSupertypesR([],self.targetUnit.getClass(self.addr2ClassName(orginList[0])))
                    if "Landroid/app/Activity;" in classes or "Landroid/app/Fragment;" in classes or "Landroid/content/BroadcastReceiver;" in classes or "Landroid/content/ContentProvider;" in classes or "Landroid/app/Service;" in classes:
                        # self.fd.write("result: %s \n"%orginList)
                        self.addRoute(orginList[0],orginList)
                    # else:
                    #     self.fd.write("temp: %s \n"%orginList)
                    return None

            else:
                # process xref for overide method
                for m in oMethods:
                    method = self.targetUnit.getMethod(m)
                    if method.getAddress()+"(OVERRIDES)" in orginList:
                        # print("interface abnormal!!!!\n")
                        # self.fd.write("interface abnormal!!!!\n")
                        # return None
                        continue
                    tList = []
                    tList.extend(orginList)
                    self.asmResult(tList,method.getAddress()+"(OVERRIDES)",dAddr)
                    self.findXrefR(maxDeepth+1,tList,method.getItemId(),method.getAddress(),self.addr2ClassName(method.getAddress()))
                    # return None
            return None
            
        for method in list(s):
            # print("%s method %s\n"%(maxDeepth,method))
            tList = []
            tList.extend(orginList)
            self.asmResult(tList,method.getAddress(),dAddr)
            # print("xref %s" % method.getAddress())
            self.findXrefR(maxDeepth+1 ,tList,method.getItemId(),method.getAddress())
            # return None
        return None

    # def findOverideClassXrefProperly(self,maxDeepth,orginList,dId,dAddr,overideClassName):
    #     xrefs = self.searchWithCache(0, dId, dAddr)
    #     s = set()
    #     # prevent for finding xref like "super.onxxx(overide)" to mismatch other subclasses
    #     print("xref %s"%xrefs)
    #     print("orginList %s"%orginList)
    #     for t in xrefs:
    #         methodAddr = self.addr2Sign(t)
    #         if methodAddr == dAddr:
    #             continue
    #         if methodAddr in orginList or "Ljava" in self.addr2ClassName(t) or "Landroid" in self.addr2ClassName(t):
    #             continue
    #         clz = self.targetUnit.getClass(self.addr2ClassName(t))
    #         sClasses = set()
    #         supers = self.getClassSupertypesR([],clz)
    #         impls = self.getImplementedInterfacesR([],clz)
    #         for s1 in supers:
    #             sClasses.add(s1) 
    #         for s2 in impls:
    #             sClasses.add(s2)            
    #         print("method: %s\n sclasses: %s\n"%(methodAddr,sClasses))
    #         if overideClassName not in sClasses:
    #             s.add(self.targetUnit.getMethod(self.addr2Sign(t)))
    #         else: 
    #             print("filter %s"%self.addr2Sign(t))

    #     for method in list(s):
    #         # print("%s method %s\n"%(maxDeepth,method))
    #         tList = []
    #         tList.extend(orginList)
    #         self.asmResult(tList,method.getAddress(),dAddr)
    #         # print("xref %s" % method.getAddress())
    #         self.findXrefR(maxDeepth+1 ,tList,method.getItemId(),method.getAddress())
    #         # return None
    
    def findClousureClassXref(self,maxDeepth,orginList,dAddr,specialClassName):
        '''
        find implemented class xref-caller
        '''
        clz = self.targetUnit.getClass(self.addr2ClassName(dAddr))
        if clz is None:
            return False
        # print(clz.getImplementedInterfaces())
        prefix = "(%s)"%specialClassName.split('/')[-1].upper()
        sClasses = set()
        supers = self.getClassSupertypesR([],clz)
        impls = self.getImplementedInterfacesR([],clz)
        for s1 in supers:
            sClasses.add(s1) 
        for s2 in impls:
            sClasses.add(s2)
        # for c in sClasses:
        if specialClassName in sClasses:
            # print ("match %s"%clz)
            clz = self.targetUnit.getClass(self.addr2ClassName(dAddr))
            if clz.getAddress()+prefix in orginList :
                # self.fd.write("abnormal %s\n"%specialClassName)
                # self.fd.write("abnormal %s\n"%specialClassName)
                return False
                # break
            tList = []
            tList.extend(orginList)
            self.asmResult(tList,clz.getAddress()+prefix,dAddr)
            # self.asmResult(tList,dAddr+prefix,dAddr)
            # print(dAddr+prefix)
            ### special filter for Runnable classes
            xrefs = self.searchWithCache(0, clz.getItemId(), clz.getAddress())
            methodsCallOriginClass = set()
            for t in xrefs:
                if clz.getAddress() != self.addr2ClassName(t):
                    methodsCallOriginClass.add(self.targetUnit.getMethod(self.addr2Sign(t)))
            # print("methodsCallOriginClass %s"%methodsCallOriginClass)
            for method in list(methodsCallOriginClass):
                # if method.getAddress() == dAddr:
                #     continue
                if method.getAddress() in tList:
                    # self.fd.write("abnormal at end %s\n"%specialClassName)
                    return False
                    # continue
                tList1 = []
                tList1.extend(tList)
                self.asmResult(tList1,method.getAddress(),dAddr+prefix)
                # self.fd.write("strange: %s\n"%tList1)
                self.findXrefR(maxDeepth,tList1,method.getItemId(),method.getAddress())
            return True
        return False

    def findParentMethods(self, methodAddr):
        # print("findParent %s" % methodAddr)
        m = self.targetUnit.getMethod(methodAddr)
        overidesList = self.searchWithCache(1, m.getItemId(), m.getAddress())
        
        if overidesList:
            clz = self.targetUnit.getClass(self.addr2ClassName(methodAddr))
            if clz is None:
                return []
            clzList = clz.getImplementedInterfaces()
            clzList.extend(clz.getSupertypes())
            clzList = map(lambda a:a.getAddress(),clzList)
            r = []
            
            # filter
            for mtda in overidesList:
                if self.addr2ClassName(mtda) in clzList and "Ljava" not in self.addr2ClassName(mtda) and "Landroid" not in self.addr2ClassName(mtda):
                    r.append(mtda)
            return r 
        return [] 