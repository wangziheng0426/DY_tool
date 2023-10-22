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
import os
import JpyModules
import xgenm.xgGlobal as xgg
import xgenm as xg
#相机导fbx
def J_resourceSetupTool_init():
    cmds.treeView( 'J_loadCache_TreeView', edit=True, removeAll = True )
    #读取一个目录，和下面的缓存
    inputFolder= cmds.fileDialog2(fileMode=2)[0]
    if inputFolder!=None: 
        inputFolder=inputFolder[0]
    else:
        return
    cmds.textField('J_resourceSetupTool_abcPath',e=1,text=inputFolder)
    #如果设置了资产目录则使用，未设置则先分析资产目录
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1)
    if not os.path.exists(assetsPath):
        assetsPath =inputFolder.split('/series/')[0]+"/assets"        
    if os.path.exists(assetsPath):
        cmds.textField('J_resourceSetupTool_assetsPath',e=1,text=assetsPath)
    else :
        print(u'未设置资产目录')
        return
    #搜多目录下的文件夹，创建ui，并读取缓存
    for item in os.listdir(inputFolder):
        if os.path.isdir(inputFolder+"/"+item):
            for item1 in os.listdir(inputFolder+"/"+item):
                if item1.lower().endswith(".abc"):
                    J_resourceSetupTool_addItem(inputFolder+"/"+item,item)
                    break
def J_resourceSetupTool_addItem(cacheAssetPath,assetName,subPathName=['chr','prp']):
    #添加每个角色作为根目录    
    cacheFolderName=assetName
    refNodeName=assetName.split('@')[-1]
    cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(cacheFolderName, "") )
    #assetName ：chr_yeChenZYZ@yeChenZYZRN 从中解析出角色名
    assetType=assetName.split('@')[0].split('_')[0]
    assetName=assetName.split('@')[0].split('_')[-1]
    fileFoundState=0
    #先搜索模型文件和毛发文件
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1)
    #仅搜索chr文件夹和prp文件夹
    currentAsset=''
    if not os.path.exists(assetsPath):
        print(u'未找到资产目录')

    if os.path.exists(assetsPath+"/"+assetType):
        #查找所有资产文件夹
        for fItem in os.listdir(assetsPath+"/"+assetType):
            #判断是资产目录
            if os.path.isdir(assetsPath+"/"+assetType+'/'+fItem):
                #资产目录名与缓存文件夹一致
                if fItem==assetName:
                    currentAsset=assetsPath+"/"+assetType+'/'+fItem
    #查找"资产名_srf"文件
    srfFilePath=currentAsset+'/srf/publish'
    
    if os.path.exists(srfFilePath):
        for fItem1 in os.listdir(srfFilePath):
            if fItem1.endswith('.ma') or fItem1.endswith('.mb') :
                if os.path.splitext(fItem1)[0]==assetName+'_srf':
                    srfFilePath=srfFilePath+'/'+fItem1
                    fileFoundState=1
                    break
    #如果找到模型文件，则添加子控件
        if os.path.isfile(srfFilePath):
        #添加绑定
            cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(refNodeName+"@"+srfFilePath, cacheFolderName) )
            #cmds.treeView('J_loadCache_TreeView',edit=1, image=(srfFilePath, 1,'createReference.png') )
            cmds.treeView('J_loadCache_TreeView',edit=1, image=(refNodeName+"@"+srfFilePath, 1,'nClothDisplayCurrent.png') )
    #查找"资产名_cfx"文件
    cfxFilePath=currentAsset+'/cfx/publish'
    if os.path.exists(cfxFilePath):
        for fItem1 in os.listdir(cfxFilePath):
            if fItem1.endswith('.ma') or fItem1.endswith('.mb') :
                if os.path.splitext(fItem1)[0]==assetName+'_cfx':
                    cfxFilePath=cfxFilePath+'/'+fItem1
                    fileFoundState=1
                    break
    #如果找到模型文件，则添加子控件
        if os.path.isfile(cfxFilePath):
            cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(refNodeName+"@"+cfxFilePath, cacheFolderName) )
            #cmds.treeView('J_loadCache_TreeView',edit=1, image=(cfxFilePath, 1,'createReference.png') )
            cmds.treeView('J_loadCache_TreeView',edit=1, image=(refNodeName+"@"+cfxFilePath, 1,'hairConvertHairSystem.png') )

    #设置按钮显示状态
    iconList=['error.png','precompExportChecked.png']
    cmds.treeView('J_loadCache_TreeView',edit=1, image=(cacheFolderName, 1,iconList[fileFoundState]) )
    #cmds.treeView('J_loadCache_TreeView',edit=1, image=(assetName, 2,'createCache.png') )
    cmds.treeView('J_loadCache_TreeView',edit=1, pressCommand=[(1,J_resourceSetupTool_refFile) ])

#按钮功能 文件存在则加载
def J_resourceSetupTool_refFile(*args):
    itemInfo=cmds.treeView('J_loadCache_TreeView',q=1,children=args[0])
    
    for item in itemInfo:
        fileName=os.path.splitext(os.path.basename(item.split('@')[-1]))[0]

        if os.path.exists(item.split('@')[-1])  :        
            refFile=cmds.file(item.split('@')[-1], reference=True, mergeNamespacesOnClash=False, namespace=fileName) 
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
                if fItem1.endswith('_ani.abc') and fItem1.find(fileName.replace('_srf','_ani'))>-1 :
                    animAbcfile=abcPath+"/"+fItem1
                    #print animAbcfile
                    cmds.AbcImport(abcPath+"/"+fItem1 ,mode= 'import' ,connect =(modelNameSpace+":srfNUL"),createIfNotFound=1)
                if fItem1.endswith('_sim.abc') and fItem1.find(fileName.replace('_cfx','_sim'))>-1 :
                    simAbcFile=abcPath+"/"+fItem1
                    #print simAbcFile
                    cmds.AbcImport(abcPath+"/"+fItem1 ,mode= 'import' ,connect =(modelNameSpace+":simNUL"),createIfNotFound=1)
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
        

def J_resourceSetupTool_saveSetting():
    pass
if __name__=='__main__':
    J_resourceSetupTool_init()