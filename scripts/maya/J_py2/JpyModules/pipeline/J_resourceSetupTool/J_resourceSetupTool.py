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
    assetName=cacheFolderName.split('@')[0].split('_')[-1]
    fileFoundState=0
    #新机制，先读取jcl文件，如果没有jcl或者jcl记录的文件不存在，则搜索资产目录
    abcJcl='.jcl'
    for fileItem in os.listdir(cacheAssetPath):
        if fileItem.endswith('.jcl'):
            ofile=open(cacheAssetPath+'/'+fileItem,'r')
            abcJcl=json.load(ofile)
            ofile.close()
            break
    #读取jcl中的字段，按照绑定目录查找
    srfFile=abcJcl['0']['referenceFile'][0].lower().replace('rig','srf')
    #设置帧率，时间线
    cmds.currentUnit(time=abcJcl["settings"]["frameRate"])
    cmds.playbackOptions(minTime=abcJcl["settings"]["frameRange"][0])
    cmds.playbackOptions(maxTime=abcJcl["settings"]["frameRange"][1])
    #如果不对，则尝试替换工程目录
    if not os.path.exists(srfFile):
        srfFile=srfFile.replace(abcJcl['settings']['projectPath'].lower(),cmds.workspace(q=1,rd=1)[0:-1].lower())
    #如果还是找不到文件，则尝试替换后缀
    if not os.path.exists(srfFile):
        if srfFile.endswith('.mb'):
            srfFile=srfFile[:-3]+'.ma'
        else:
            srfFile=srfFile[:-3]+'.mb'   
    cfxFile=abcJcl['0']['referenceFile'][0].lower().replace('rig','cfx')
    if not os.path.exists(srfFile):
        cfxFile=cfxFile.replace(abcJcl['settings']['projectPath'].lower(),cmds.workspace(q=1,rd=1)[0:-1].lower())
    if not os.path.exists(cfxFile):
        if cfxFile.endswith('.mb'):
            cfxFile=cfxFile[:-3]+'.ma'
        else:
            cfxFile=cfxFile[:-3]+'.mb'  
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
            currentAssetPath=(assetsPath+'/'+dirItem).lower()
            break
        if os.path.isdir(assetsPath+'/'+dirItem):
            for dirItem1 in os.listdir(assetsPath+'/'+dirItem):
            #资产目录名与缓存文件夹一致
                if dirItem1==assetName:
                    currentAssetPath=(assetsPath+'/'+dirItem+'/'+dirItem1).lower()
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
                        srfFile=(root.replace('\\','/')+'/'+item).lower()
                        
                        break
        print (assetName+u"缓存文件中资产信息无效，自动识别："+srfFile)                
    #找毛发cfx文件
    if not os.path.exists(cfxFile):
        for root,dirs,files in os.walk(currentAssetPath):
            for item in files:
                if os.path.splitext(item)[0]==assetName+"_cfx":
                    if item.endswith('.ma') or item.endswith('.mb'):
                        cfxFile=(root.replace('\\','/')+'/'+item).lower()
                        
                        break
        print (assetName+u"缓存文件中资产信息无效，自动识别："+cfxFile)
    #如果没找到模型文件，则创建站位名称
    srfstate='nClothDisplayCurrent.png'
    cfxstate='hairConvertHairSystem.png'
    if not os.path.exists(srfFile):
        srfFile=cacheFolderName+"_srfFile"
        srfstate='error.png'
    if not os.path.exists(cfxFile):
        cfxFile=cacheFolderName+"_cfxFile"
        cfxstate='error.png'
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
            refFile=cmds.file(item.split('$')[-1], reference=True, mergeNamespacesOnClash=False, namespace=fileName) 
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
                #将abc缓存merge到模型
                if fItem1.endswith('_ani.abc') and fItem1.lower().find(fileName.replace('_srf','_ani'))>-1 :
                    animAbcfile=abcPath+"/"+fItem1
                    #print animAbcfile
                    print (modelNameSpace+":srfNUL")
                    cmds.AbcImport(animAbcfile ,mode= 'import' ,connect =(modelNameSpace+":srfNUL"),createIfNotFound=1)
                if fItem1.endswith('_sim.abc') and fItem1.lower().find(fileName.replace('_cfx','_sim'))>-1 :
                    simAbcFile=abcPath+"/"+fItem1
                    #print simAbcFile
                    cmds.AbcImport(simAbcFile,mode= 'import' ,connect =(modelNameSpace+":simNUL"),createIfNotFound=1)
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
                                    print (description+u":加载abc")
                                    xg.setAttr('useCache','true',palette,description,'SplinePrimitive')
                                    xg.setAttr('cacheFileName',str(abcPath+"/"+fItem1) ,str(palette),str(description),'SplinePrimitive')
                                    de = xgg.DescriptionEditor
                                    de.refresh("Full")
        else:
            print (u'未找到资产：'+item.split('@')[-1])
        


if __name__=='__main__':
    J_resourceSetupTool_loadFile()