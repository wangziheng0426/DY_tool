# -*- coding:utf-8 -*-
##  @package J_resourceSetupTool
#
##  @brief   
##  @author 桔
##  @version 1.0
##  @date  4:03 2023/10/16
#  History:  

import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om2
import os,json
import JpyModules
import xgenm.xgGlobal as xgg
import xgenm as xg

def J_resourceSetupTool_init():
    cmds.treeView( 'J_loadCache_TreeView', edit=True, removeAll = True )
    cmds.textField('J_resourceSetupTool_assetsPath',e=1,\
            changeCommand=JpyModules.pipeline.J_resourceSetupTool.J_resourceSetupTool_changeSetting)
    cmds.treeView('J_loadCache_TreeView',edit=1, contextMenuCommand=\
                  JpyModules.pipeline.J_resourceSetupTool.J_projectManeger_popupMenuCommand )
                #J_projectManeger_popupMenuCommand )
    cmds.button('J_rs_loadCache',e=1,c=J_resourceSetupTool_refAllFile)
    #右键菜单
    popm=cmds.popupMenu(parent='J_loadCache_TreeView')
    cmds.menuItem(parent=popm,label=u"添加资产文件" ,\
                  c=JpyModules.pipeline.J_resourceSetupTool.J_resourceSetupTool_addTreeItem)
    cmds.menuItem(parent=popm,label=u"删除资产",\
                  c=JpyModules.pipeline.J_resourceSetupTool.J_resourceSetupTool_removeItem)
    
    j_meta=JpyModules.pipeline.J_meta(cmds.workspace(q=1,rd=1)[0:-1],cmds.workspace(q=1,rd=1)[0:-1])
    if j_meta.metaInfo["userInfo"].has_key('assetPath'):        
        cmds.textField('J_resourceSetupTool_assetsPath',e=1,\
                       text=(cmds.workspace(q=1,rd=1)[0:-1]+j_meta.metaInfo["userInfo"]['assetPath']))

def J_resourceSetupTool_changeSetting(*arg):
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1).replace('\\','/')
    cmds.textField('J_resourceSetupTool_assetsPath',e=1,text=assetsPath)
   
    
def J_projectManeger_popupMenuCommand(*arg):
    cmds.treeView('J_loadCache_TreeView',e=1, clearSelection=1)
    if cmds.treeView('J_loadCache_TreeView',q=1, itemExists=arg[0]):
        cmds.treeView('J_loadCache_TreeView',e=1, selectItem=(arg[0],True))
    return True
def J_resourceSetupTool_removeItem(*arg):
    sel=cmds.treeView('J_loadCache_TreeView',q=1, selectItem=1)  
    if len(sel)>0:  
        pitem=cmds.treeView('J_loadCache_TreeView',q=1, itemParent=sel[0] )
        if pitem!='':
            cmds.treeView('J_loadCache_TreeView',e=1, removeItem=sel[0] )
def J_resourceSetupTool_addTreeItem(*arg):
    sel=cmds.treeView('J_loadCache_TreeView',q=1, selectItem=1)  
    if sel==None:return
    if len(sel)>0:  
        pitem=cmds.treeView('J_loadCache_TreeView',q=1, itemParent=sel[0] )
        if pitem=='':
            mayaFile= cmds.fileDialog2(fileMode=1)
            if mayaFile!=None: 
                mayaFile=mayaFile[0]
            else:
                return
            cmds.treeView('J_loadCache_TreeView',e=1, addItem=(sel[0]+'$'+mayaFile, sel[0]) )
            cmds.treeView('J_loadCache_TreeView',edit=1, displayLabel=(sel[0]+'$'+mayaFile, mayaFile) )

            state='nClothDisplayCurrent.png'
            if os.path.splitext(mayaFile)[0].endswith('cfx'):
                state='hairConvertHairSystem.png'
            cmds.treeView('J_loadCache_TreeView',edit=1, image=(sel[0]+'$'+mayaFile, 1,state) )

def J_resourceSetupTool_loadFile():
    cmds.treeView( 'J_loadCache_TreeView', edit=True, removeAll = True )
    #读取缓存目录
    inputFolder= cmds.fileDialog2(fileMode=2)
    if inputFolder!=None: 
        inputFolder=inputFolder[0]
    else:
        return
    cmds.textField('J_resourceSetupTool_abcPath',e=1,text=inputFolder)
    #读取用户设置的资产目录
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1)
    #如果目录不存在，则尝试加载工程的jmeta，从工程信息解析资产目录
    if not os.path.exists(assetsPath):
        j_meta=JpyModules.pipeline.J_meta(cmds.workspace(q=1,rd=1)[0:-1])
        if j_meta.metaInfo['userInfo'].has_key('assetPath'):            
            assetsPath=cmds.workspace(q=1,rd=1)[0:-1]+j_meta.metaInfo['userInfo']['assetPath']    
            cmds.textField('J_resourceSetupTool_assetsPath',e=1,text=assetsPath)
    if not os.path.exists(assetsPath):
        print(u'资产目录有误，或者不存在')
        return
    #搜目录下的文件夹，创建ui，并读取缓存,如果存在配套jcl，则优先读取jcl
    for item in os.listdir(inputFolder):
        if os.path.isdir(inputFolder+"/"+item):
            for item1 in os.listdir(inputFolder+"/"+item):
                if item1.lower().endswith(".abc"):
                    J_resourceSetupTool_addItem(inputFolder+"/"+item,item)
                    break

def J_resourceSetupTool_addItem(cacheAssetPath,cacheFolderName):
    #添加每个角色作为根目录    
    refNodeName=cacheFolderName.split('@')[-1]
    #每个文件都会对应生成两个资产条目，如果找不到文件，则置空，并提示
    cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(cacheFolderName, "") )
    cmds.treeView('J_loadCache_TreeView',edit=1, image=(cacheFolderName, 1,'precompExportChecked.png') )
    #assetName ：chr_yeChenZYZ@yeChenZYZRN 从中解析出角色名
    assetType=cacheFolderName.split('@')[0].split('_')[0]
    
    assetName='_'.join(cacheFolderName.split('@')[0].split('_')[1:])
    print (u'分析目录得到'+assetType+u'类型资产文件:'+assetName)
    fileFoundState=0
    #新机制，先读取jcl文件，如果没有jcl或者jcl记录的文件不存在，则搜索资产目录
    abcJcl='.jcl'
    print (u'搜索缓存日志文件')
    for fileItem in os.listdir(cacheAssetPath):
        if fileItem.endswith('.jcl'):
            print (u'找到日志文件:'+fileItem)
            ofile=open(cacheAssetPath+'/'+fileItem,'r')
            abcJcl=json.load(ofile)
            ofile.close()
            break

    #读取jcl中的字段，按照绑定目录查找
    srfFile=getCustomFilePath(abcJcl['0']['referenceFile'][0],'rig','srf')
    #返回为空就是没找到，有可能是解算文件导出的，用rigsol尝试
    if srfFile=='':
        print (u'没找到rig资产，可能文件是rigsol导出')
        srfFile=getCustomFilePath(abcJcl['0']['referenceFile'][0],'cfx_rigsol','srf')
        print (u'搜索rigsol文件：'+srfFile)

    #设置帧率，时间线
    cmds.currentUnit(time=abcJcl["settings"]["frameRate"])
    cmds.playbackOptions(minTime=abcJcl["settings"]["frameRange"][0])
    cmds.playbackOptions(maxTime=abcJcl["settings"]["frameRange"][1])
    #如果找不到文件，则尝试替换工程目录
    if not os.path.exists(srfFile):
        srfFile=srfFile.replace(abcJcl['settings']['projectPath'],cmds.workspace(q=1,rd=1)[0:-1])
    # #如果还是找不到文件，则尝试替换后缀
    # if not os.path.exists(srfFile):
    #     if srfFile.endswith('.mb'):
    #         srfFile=srfFile[:-3]+'.ma'
    #     else:
    #         srfFile=srfFile[:-3]+'.mb'   
        
    cfxFile=getCustomFilePath(abcJcl['0']['referenceFile'][0],'rig','cfx')
    #返回为空就是没找到，有可能是解算文件导出的，用rigsol尝试
    if cfxFile=='':
        print (u'没找到rig资产，可能文件是rigsol导出')
        cfxFile=getCustomFilePath(abcJcl['0']['referenceFile'][0],'cfx_rigsol','cfx')
        print (u'搜索rigsol文件：'+cfxFile)

    if not os.path.exists(cfxFile):
        cfxFile=cfxFile.replace(abcJcl['settings']['projectPath'],cmds.workspace(q=1,rd=1)[0:-1])  
    #如果根据jcl找不到文件，则从窗口设置的目录中搜索
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1)

    
    if not os.path.exists(assetsPath):
        print(u'资产目录不存在，或者设置有误')
    
    #先找当前资产目录
    currentAssetPath=''
    #搜索资产目录下的文件，为了防止文件过多等待过久，仅向下找两层
    found=0
    for dirItem in os.listdir(assetsPath):
        if dirItem==assetName:
            currentAssetPath=(assetsPath+'/'+dirItem)
            break
        if os.path.isdir(assetsPath+'/'+dirItem):
            for dirItem1 in os.listdir(assetsPath+'/'+dirItem):
            #资产目录名与缓存文件夹一致
                if dirItem1==assetName:
                    currentAssetPath=(assetsPath+'/'+dirItem+'/'+dirItem1)
                    found=1
                    break
        if found:
            break
    
    
    #如果之前通过jcl没找到，则从当前资产文件夹里寻找"_srf"文件,如果文件夹中有多个同名srf，只读取第一个
    if not os.path.exists(srfFile):
        for root,dirs,files in os.walk(currentAssetPath):
            for item in files:
                if os.path.splitext(item)[0]==assetName+"_srf":
                    if item.endswith('.ma') or item.endswith('.mb'):
                        srfFile=(root.replace('\\','/')+'/'+item)
                        
                        break
        print (assetName+u"缓存文件中资产信息无效，自动识别："+srfFile)                
    #找毛发cfx文件
    if not os.path.exists(cfxFile):
        for root,dirs,files in os.walk(currentAssetPath):
            for item in files:
                if os.path.splitext(item)[0]==assetName+"_cfx":
                    if item.endswith('.ma') or item.endswith('.mb'):
                        cfxFile=(root.replace('\\','/')+'/'+item)
                        
                        break
        print (assetName+u"缓存文件中资产信息无效，自动识别："+cfxFile)
    #如果没找到模型文件，则创建站位名称
    srfstate='nClothDisplayCurrent.png'
    cfxstate='hairConvertHairSystem.png'
    if not os.path.exists(srfFile):        
        srfstate='error.png'
        print (u'未找到资产：'+srfFile)
        srfFile=cacheFolderName+"_srfFile"
    if not os.path.exists(cfxFile):        
        cfxstate='error.png'
        print (u'未找到资产：'+cfxFile)
        cfxFile=cacheFolderName+"_cfxFile"
    #添加绑定
    cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(cacheFolderName+'$'+srfFile, cacheFolderName) )
    cmds.treeView('J_loadCache_TreeView',edit=1, displayLabel=(cacheFolderName+'$'+srfFile, srfFile) )
    cmds.treeView('J_loadCache_TreeView',edit=1, image=(cacheFolderName+'$'+srfFile, 1,srfstate) )

    #cfx动力学
    
    cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(cacheFolderName+'$'+cfxFile, cacheFolderName) )
    cmds.treeView('J_loadCache_TreeView',edit=1, displayLabel=(cacheFolderName+'$'+cfxFile, cfxFile) )
    cmds.treeView('J_loadCache_TreeView',edit=1, image=(cacheFolderName+'$'+cfxFile, 1,cfxstate) )
    
    #设置按钮显示状态
    #'error.png','precompExportChecked.png'
    cmds.treeView('J_loadCache_TreeView',edit=1, pressCommand=[(1,J_resourceSetupTool_refFile) ])
    #cmds.treeView('J_loadCache_TreeView',edit=1, itemRenamedCommand=\
                  #JpyModules.pipeline.J_resourceSetupTool.J_resourceSetupTool_resetTreeItem)


#按钮功能 文件存在则加载
def J_resourceSetupTool_refFile(*args):
    itemInfo=cmds.treeView('J_loadCache_TreeView',q=1,children=args[0])
    #pitem=cmds.treeView('J_loadCache_TreeView',q=1, itemParent=sel[0] )
    for item in itemInfo:
        print (u'引入文件：'+ item.split('$')[-1])
        fileName=os.path.splitext(os.path.basename(item.split('$')[-1]))[0]

        if os.path.exists(item.split('$')[-1])  :        
            refFile=cmds.file(item.split('$')[-1], reference=True,prompt=0, mergeNamespacesOnClash=False, namespace=fileName) 
            print (refFile+u'文件已导入')
            refNode=cmds.referenceQuery(refFile,referenceNode=True)
            #名字空间默认带冒号去掉开头的冒号
            modelNameSpace=cmds.referenceQuery(refNode,namespace=True)
            if modelNameSpace.startswith(":"):
                modelNameSpace=modelNameSpace[1:]
            #print modelNameSpace
            #合并abc到模型节点 ，根据记录的abc目录 和列表分析出的角色名，找到abc
            abcPath=cmds.textField('J_resourceSetupTool_abcPath',q=1,text=1)
            #通过父层获取角色名
            abcCacheFolderName=cmds.treeView('J_loadCache_TreeView',q=1, itemParent=item )

            abcPath+='/'+abcCacheFolderName
            animAbcfile=''
            simAbcFile=''
            for fItem1 in os.listdir(abcPath):
                #将abc缓存merge到模型,如果导出的时候带有jcl信息，那么根据导出的时候选择的节点进行指认
                if fItem1.endswith('_ani.abc') and fItem1.lower().find(fileName.lower().replace('_srf','_ani'))>-1 :
                    animAbcfile=abcPath+"/"+fItem1                    
                    nodeToMergeAbc=(modelNameSpace+":srfNUL")
                    jclFile=animAbcfile[:-4]+'_Log.jcl'
                    jclstr=''
                    if os.path.exists(jclFile):
                        ofile=open(jclFile,'r')
                        jclstr=json.load(ofile)
                        ofile.close()
                    
                        if cmds.objExists(modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1]):
                            nodeToMergeAbc=modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1]
                            print (u'使用jcl文件中读取到的节点：'+nodeToMergeAbc)
                        else:
                            print ((modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1])+u'未找到')
                    else:
                        print (jclFile+u'没找到')
                    if cmds.objExists(nodeToMergeAbc):   
                        cmds.AbcImport(animAbcfile,mode= 'import' ,connect =nodeToMergeAbc)       
                        #commandToR='cmds.AbcImport("'+animAbcfile+'" ,mode="import" ,connect ="'+nodeToMergeAbc+'")'
                        #cmds.evalDeferred(commandToR)
                        print (u'使用abc：'+animAbcfile+u' merge到'+nodeToMergeAbc)
                    else:
                        print (nodeToMergeAbc+u'未找到')
                    
                if fItem1.endswith('_sim.abc') and fItem1.lower().find(fileName.lower().replace('_cfx','_sim'))>-1 :
                    simAbcFile=abcPath+"/"+fItem1
                    nodeToMergeAbc=(modelNameSpace+":simNUL")
                    jclFile=simAbcFile[:-4]+'.jcl'
                    jclstr=''
                    if os.path.exists(jclFile):
                        ofile=open(jclFile,'r')
                        jclstr=json.load(ofile)
                        ofile.close()
                        if cmds.objExists(modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1]):
                            nodeToMergeAbc=modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1]
                            print (u'使用jcl文件中读取到的节点：'+nodeToMergeAbc)
                        else:
                            print ((modelNameSpace+':'+jclstr['0']['selectedNode'][0].split(':')[-1])+u'未找到')
                    else:
                        print (jclFile+u'没找到')        
                    
                    if cmds.objExists(nodeToMergeAbc):     
                        cmds.AbcImport(simAbcFile,mode= 'import' ,connect =nodeToMergeAbc) 
                        print (u'使用abc：'+simAbcFile+u'merge到'+nodeToMergeAbc)  
                        #commandToR='cmds.AbcImport("'+simAbcFile+'" ,mode="import" ,connect ="'+nodeToMergeAbc+'",createIfNotFound=1)'
                        #cmds.evalDeferred(commandToR)
                    else:
                        print (nodeToMergeAbc+u'未找到')
            #自动加载xgen曲线
            if xgg.Maya:
                palettes = xg.palettes()
                for palette in palettes:
                    
                    if palette.find(modelNameSpace)>-1:                    
                        print ("Collection:" + palette)
                        descriptions = xg.descriptions(palette)
                        for description in descriptions:  
                            #先关闭所有缓存，避免xgen报错
                            xg.setAttr('useCache','false',palette,description,'SplinePrimitive')
                            xg.setAttr('liveMode','false',palette,description,'SplinePrimitive')                              
                            #abc名称匹配xgen描述，相符则加载缓存
                            for fItem1 in os.listdir(abcPath):
                                if description.find(fItem1.replace('_OutputCurves.abc',''))>-1:
                                    print (description+u":加载abc->"+fItem1)
                                    xg.setAttr('useCache','true',palette,description,'SplinePrimitive')
                                    xg.setAttr('cacheFileName',str(abcPath+"/"+fItem1) ,str(palette),str(description),'SplinePrimitive')
                                    de = xgg.DescriptionEditor
                                    de.refresh("Full")
        else:
            print (u'未找到资产：'+item.split('@')[-1])
#一键加载
def J_resourceSetupTool_refAllFile(*args):
    for item in cmds.treeView('J_loadCache_TreeView',q=1,children=''):
        if len(item.split('$'))==2:
            J_resourceSetupTool_refFile(item)
def getCustomFilePath(inpath,itemA,itemB):
    inpath=inpath.replace('\\','/')
    #先搜索源目录    
    resPath=os.path.dirname(inpath)
    print (u'搜索目录：'+resPath)
    pathsplitNum= resPath.lower().find('/'+itemA.lower())
    #实际目录中的名字
    iATemp=''
    iBTemp=''
    #找到源目录上层后，逐个比对是否符合目标目录
    if pathsplitNum>-1:        
        resPath=inpath[:pathsplitNum]
        if os.path.exists(resPath):
            for fItem in os.listdir(resPath):
                if os.path.isdir(resPath+'/'+fItem):
                    if fItem.lower()== itemA:                    
                        iATemp=fItem
                    if fItem.lower()== itemB: 
                        iBTemp=fItem       
        resPath=os.path.dirname(inpath).replace(iATemp,iBTemp)
        print(u'找到匹配的资产目录：'+resPath)
        #匹配文件名
    #如果是解算文件导出的缓存，会带有CFX_rigsol
    if itemA=='cfx_rigsol':
        characterPath=resPath[:resPath.lower().find('/cfx')]
        for tfItem in os.listdir(characterPath):
            if tfItem.lower()==itemB:
                resPath=os.path.dirname(resPath)+'/'+tfItem
                print (u'从解算目录解析到'+itemB+u'目录:'+resPath)

    if os.path.exists(resPath):
        #为了兼容cgt的目录结构，除了当前类型资产目录，再向下找一层目录
        fileNotFound=True
        for l0fItem in os.listdir(resPath):  
            if l0fItem.lower().endswith('.mb') or l0fItem.lower().endswith('.ma'):
                if l0fItem.lower()==os.path.basename(inpath).lower().replace(itemA,itemB):
                    resPath=resPath+'/'+l0fItem
                    fileNotFound=False
                    break
        if  fileNotFound:   
            for l0fItem in os.listdir(resPath):
                if os.path.isdir(resPath+'/'+l0fItem):
                    for l1fItem in  os.listdir(resPath+'/'+l0fItem):
                        if l1fItem.lower().endswith('.mb') or l1fItem.lower().endswith('.ma'):
                            if l1fItem.lower()==os.path.basename(inpath).lower().replace(itemA,itemB):
                                resPath=resPath+'/'+l0fItem+'/'+ l1fItem                            
                                break

    if os.path.exists(resPath):
        if os.path.isfile(resPath):
            print (u"找到资产："+resPath)
            return resPath
        else:
            return ''
    else:
        return ''

if __name__=='__main__':
    J_resourceSetupTool_loadFile()