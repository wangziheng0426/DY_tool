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
import re,os
import JpyModules
#相机导fbx
def J_resourceSetupTool_init():
    cmds.treeView( 'J_loadCache_TreeView', edit=True, removeAll = True )
    #读取一个目录，和下面的缓存
    inputFolder= cmds.fileDialog2(fileMode=2,startingDirectory=r'Z:\XWDZ\series\shots\ss01\ep21\s007\c0009\ani\publish\v001\cache')[0]
    #如果设置了资产目录则世界使用，未设置则先分析资产目录
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
    #添加每个角色的总目录
    cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(assetName, "") )
    fileFoundState=0
    #先搜索模型文件和毛发文件
    assetsPath=cmds.textField('J_resourceSetupTool_assetsPath',q=1,text=1)
    #仅搜索chr文件夹和prp文件夹
    currentAsset=''
    if not os.path.exists(assetsPath):
        print(u'未找到资产目录')
    for item in subPathName:
        if os.path.exists(assetsPath+"/"+item):
            #查找所有资产文件夹
            for fItem in os.listdir(assetsPath+"/"+item):
                #判断是资产目录
                if os.path.isdir(assetsPath+"/"+item+'/'+fItem):
                    #资产目录名与缓存文件夹一致
                    if fItem==assetName:
                        currentAsset=assetsPath+"/"+item+'/'+fItem
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
            cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(srfFilePath, assetName) )
            #cmds.treeView('J_loadCache_TreeView',edit=1, image=(srfFilePath, 1,'createReference.png') )
            cmds.treeView('J_loadCache_TreeView',edit=1, image=(srfFilePath, 1,'nClothDisplayCurrent.png') )
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
            cmds.treeView('J_loadCache_TreeView',edit=1, addItem=(cfxFilePath, assetName) )
            #cmds.treeView('J_loadCache_TreeView',edit=1, image=(cfxFilePath, 1,'createReference.png') )
            cmds.treeView('J_loadCache_TreeView',edit=1, image=(cfxFilePath, 1,'hairConvertHairSystem.png') )

    #设置按钮显示状态
    iconList=['error.png','precompExportChecked.png']
    cmds.treeView('J_loadCache_TreeView',edit=1, image=(assetName, 1,iconList[fileFoundState]) )
    #cmds.treeView('J_loadCache_TreeView',edit=1, image=(assetName, 2,'createCache.png') )
    cmds.treeView('J_loadCache_TreeView',edit=1, pressCommand=[(1,J_resourceSetupTool_refFile) ])
def J_resourceSetupTool_refFile(*args):
    itemInfo=cmds.treeView('J_loadCache_TreeView',q=1,children=args[0])
    if len(itemInfo)>1:
        for item in itemInfo[1:]:
            fileName=os.path.splitext(os.path.basename(item))[0]
            cmds.file(item, reference=True, mergeNamespacesOnClash=False, namespace=fileName) 
    else:
        fileName=os.path.splitext(os.path.basename(args[0]))[0]
        cmds.file(args[0], reference=True, mergeNamespacesOnClash=False, namespace=fileName)
if __name__=='__main__':
    J_resourceSetupTool_init()