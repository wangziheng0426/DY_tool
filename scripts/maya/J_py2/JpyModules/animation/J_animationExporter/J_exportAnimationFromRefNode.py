# -*- coding:utf-8 -*-
##  @package J_animationExporter
#
##  @brief   
##  @author 桔
##  @version 1.0
##  @date   12:03 2022/5/20
#  History:  

import re
import os
import maya.cmds as cmds
import maya.mel as mel
import maya.api.OpenMaya as om2
import shutil
import JpyModules
def J_exportAnimationFromRefNode(refNode,outPath='',exportFacial=False,jointOnly=False):
    cmds.lockNode("initialShadingGroup", l=0, lu=0)
    startFrame=cmds.playbackOptions( query=1, minTime=1)
    endFrame=cmds.playbackOptions( query=1, maxTime=1)
    if (outPath==''):
        #文件路径
        filePath=JpyModules.public.J_getMayaFileFolder()+'/'    
        #文件名
        fileName=JpyModules.public.J_getMayaFileNameWithOutExtension()  
        outPath=filePath+fileName+"_"+refNode+".fbx"
    if (cmds.objExists(refNode) ):        
        #如果ref未加载，则加载
        if (not cmds.referenceQuery(refNode,isLoaded=1) ):
            cmds.file(refNode,loadReferenceDepth="asPrefs",loadReference=1)
        #搜索根骨
        root=J_getRootJointFromRefNode(refNode)

        #导出所选
        if not cmds.objExists(root[0]):
            return refNode+":ref节点中没有找到骨骼"
        #如果未找到根骨则退出
        if len(root)<1:return refNode+":ref节点中没有找到骨骼"
        #修改约束方式,暂时弃用
        #allConstraint=cmds.ls(type= 'constraint')
        #for itemc in allConstraint:
        #    if cmds.objectType(itemc)=="orientConstraint" or cmds.objectType(itemc)=="parentConstraint":
        #        cmds.setAttr(itemc+".interpType"),2)

        #烘培关键帧
        cmds.bakeResults(root,t =(startFrame,endFrame),hierarchy ="below" ,simulation=1,
            sampleBy= 1 ,oversamplingRate= 1 ,disableImplicitControl =1 ,preserveOutsideKeys=1, 
            sparseAnimCurveBake=0 ,removeBakedAttributeFromLayer=0 ,removeBakedAnimFromLayer=1,
            bakeOnOverrideLayer= 0 ,minimizeRotation=1,controlPoints = 0,shape=1)           
        
        #导入ref
        refFile=cmds.referenceQuery(refNode,filename=1)
        cmds.file(refFile,importReference=1)
        #卸载其他ref
        allRefFile=cmds.file(q=1,r=1)
        for refFileitem in allRefFile:
            refNodeTemp=cmds.referenceQuery(refFileitem,referenceNode=1)
            if (refNodeTemp!=refNode):
                if cmds.referenceQuery(refNodeTemp,isLoaded=1):
                    cmds.file(refFileitem,unloadReference=1) 

        #如果最外层有其他角色骨骼则删除
        #if cmds.objExists("|Bone_Broom_01"): cmds.delete ("|Bone_Broom_01")
        #骨骼移到最外侧
        newRoot=[]
        for jointItem in root:
            if cmds.objExists(jointItem):
                parentTemp=cmds.listRelatives(jointItem,p=1)
                if parentTemp:
                    newParentTemp= cmds.parent(jointItem,w=1)
                    for newTempItem in newParentTemp:
                        newRoot.append(newTempItem)

        if len(newRoot)<1:
            print ("找不到骨骼")
            return 
        #引擎是用的片段可以仅导出动画
        if jointOnly:
            cmds.delete(cmds.ls(cmds.listHistory(newRoot),type='mesh'))
        cmds.select(newRoot)
        #关闭约束
        cmds.delete(cmds.ls(type= 'constraint'))
        
        #羽化动画曲线
        for jointItem in cmds.ls(type ='joint'):
            if cmds.checkBox('J_animationExporter_chbox01' ,q=1 ,v =1):
                cmds.filterCurve(jointItem+".rotateX",jointItem+".rotateY",jointItem+".rotateZ")
            if cmds.checkBox('J_animationExporter_chbox02' ,q=1 ,v =1):
                cmds.keyTangent((jointItem+".rotateX") (jointItem+".rotateY") (jointItem+".rotateZ"),ott= 'linear' )

        #根骨是否归零
        if cmds.checkBox('J_animationExporter_chbox03' ,q=1 ,v =1):
            for jointItem in newRoot:
                cmds.delete(cmds.listConnections(jointItem,type='animCurve'))
                cmds.setAttr(jointItem+".translateY",0) 
                cmds.setAttr(jointItem+".translateZ",0) 
                cmds.setAttr(jointItem+".rotateX",0) 
                cmds.setAttr(jointItem+".rotateY",0) 
                cmds.setAttr(jointItem+".rotateZ",0) 

        #删除名字空间
        mel.eval('J_animationExporterRemoveAllNameSpace()')
        quaternionMode=cmds.optionMenu('J_animationExporter_optionMenu01',q=1,v=1)
        J_exportToFbxFile(outPath,takeName=refNode,QuaternionMode=quaternionMode) 
        # 
        #导出表情
        if exportFacial:
            faceModels=cmds.ls("*_Face",ap=1,type='transform')
            #删除blendshape节点上的动画和模型链接
            cmds.select(cmds.ls(cmds.listHistory(faceModels),type='blendShape'))
            for item in om2. MItSelectionList(om2.MGlobal.getActiveSelectionList()):
                bsNodeFullName=item.getStrings()
                for attrItem in cmds.listAttr(bsNodeFullName[0]+".w",m=1):
                    cmds.setAttr(bsNodeFullName[0]+"."+attrItem,l=0)
                mfnDp=om2.MFnDependencyNode(item.getDependNode())
                for mPlugItem in mfnDp.getConnections():
                    if mPlugItem.source !=None:
                        #动画，模型链接都要打断
                        if mPlugItem.source().node().apiType()==296 :
                            print (mPlugItem.source().name())
                            mdf=om2.MDGModifier()
                            mdf.disconnect(mPlugItem.source(),mPlugItem)
                            mdf.doIt()
            if faceModels:
                faceModelsHis= cmds.listHistory(faceModels)
                #删除蒙皮
                cmds.delete(cmds.ls(faceModelsHis,type='skinCluster'))
                cmds.select(faceModels)
                blendNodes=cmds.ls(cmds.listHistory(faceModels),type='blendShape')
                if (blendNodes):
                    cmds.setKeyframe( blendNodes, t=[startFrame,endFrame] )
                    cmds.bakeResults( blendNodes, t=(startFrame,endFrame) ,simulation= 1)
                chName="PF_Story_"+ JpyModules.animation.J_animationExporter.J_getCharacterNeme(refFile)

                chFaceGroup=cmds.createNode('transform',n=chName)
                cmds.parent(faceModels ,chFaceGroup)
                cmds.select(chFaceGroup)

                mel.eval('FBXExportSplitAnimationIntoTakes -clear; ')   
                mel.eval('FBXExportDeleteOriginalTakeOnSplitAnimation -v true;')

                mel.eval('FBXExport -f \"'+outPath+'_Face.fbx\" -s ')
                JpyModules.animation.J_animationExporter.J_replaceSubdeformer(outPath+'_Face.fbx ')

def J_getRootJointFromRefNode(refNode):
    allNodes= cmds.referenceQuery(refNode,nodes=1)
    return J_getRootJointFromNodes(allNodes)
def J_getRootJointFromInputNodes(inputNodes):
    allNodes=cmds.listHistory(inputNodes)
    return J_getRootJointFromNodes(allNodes)
#从给定的节点中查找所有骨骼的根节点
def J_getRootJointFromNodes(allNodes):   
    if len(allNodes)<1: return [""]
    allSkinClustersFromRef=cmds.ls(allNodes ,type ='skinCluster',allPaths=1)
    if len(allSkinClustersFromRef)<1: return [""]
    skinClustersHis=cmds.listHistory(allSkinClustersFromRef)
    if len(skinClustersHis)<1: return [""]
    allJointFromSkinClusters=cmds.ls(skinClustersHis ,long=1 ,type= 'joint' )
    if len(allJointFromSkinClusters)<1: return [""]
    #refNamespace=cmds.referenceQuery(refNode,namespace=1)
    res=[]
    if len(allJointFromSkinClusters)>0:
        rootJoint=""
        for itemSC in allJointFromSkinClusters:
            rootJoint=itemSC
            par=cmds.listRelatives(itemSC,p=1,f=1)
            if len(par)>0:
                while (cmds.objectType(par[0])!="transform"):
                    rootJoint=par[0]
                    par=cmds.listRelatives(par[0],p=1,f=1)
            res.append(rootJoint)    
    return list(set(res))

def J_exportToFbxFile(outPath,takeName='take001',QuaternionMode="resample",startFrame='',endFrame=""):
    if(startFrame==""):
        startFrame=cmds.playbackOptions( query=1, minTime=1)
    if(endFrame==""):
        endFrame=cmds.playbackOptions( query=1, maxTime=1)
    #导出动画
    mel.eval('FBXResetExport ;')
    mel.eval('FBXExportInAscii  -v true')

    mel.eval('FBXExportBakeComplexAnimation -v 1; ')   
    mel.eval('FBXExportShapes -v true;')

    mel.eval('FBXExportBakeComplexStart -v '+ str(startFrame))
    mel.eval('FBXExportBakeComplexEnd -v ' +str(endFrame))

    mel.eval('FBXExportBakeResampleAnimation -v 1;')
    mel.eval('FBXExportInAscii -v 1;')

    mel.eval('FBXExportIncludeChildren -v 1;')
    mel.eval('FBXExportSplitAnimationIntoTakes -clear; ')  

    mel.eval('FBXExportDeleteOriginalTakeOnSplitAnimation -v true;')
    mel.eval('FBXExportSplitAnimationIntoTakes -v '+takeName+' '+str(startFrame) +' ' +str(endFrame))
    #曲线模式
    mel.eval('FBXExportQuaternion -v '+QuaternionMode)
    #导出
    mel.eval('FBXExport -f \"'+outPath+'\" -s ')
    #J_exportToFbxFile(outPath,takeName=refNode,QuaternionMode="resample") 
    # QuaternionMode=cmds.optionMenu('J_animationExporter_optionMenu01',q=1,v=1)

def J_exportAnimationToAbc(refNode):
    refFile=cmds.referenceQuery(refNode,filename=1 )
    finalOutPath=JpyModules.public.J_getMayaFileFolder()+"/cache"
    chName=JpyModules.animation.J_animationExporter.J_analysisAssetsName(refFile)
    fileFullName=cmds.file(query=True,sceneName=True,shortName=True)[:-3]
    cacheNameTemp='proj_'
    projectRoot=re.search('/\w*/assets',refFile)
    if projectRoot!=None:
        cacheNameTemp= projectRoot.group().replace('/assets',"").replace('/',"")+'_'
    else :
        print ("未找到工程根目录，可能资产不在assets文件夹下，请核对")
    #jishu=re.search('/s[0-9]{3}/',fileFullName)
    #if jishu!=None:
    #    cacheNameTemp+= jishu.group().replace('/',"")
    cacheNameTemp+=chName+"@"+refNode+"_ani"
    templist=[]
    for itema in cmds.referenceQuery(refNode,nodes=1):
        if itema.endswith('srfNUL'):
            templist.append(itema)
    JpyModules.public.J_exportAbc(mode=0,exportMat=False,
                                  nodesToExport=templist,
                                  cacheFileName=cacheNameTemp,
                                  j_abcCachePath=finalOutPath)
if __name__=='__main__':
    J_exportAnimationFromRefNode('RG_Nakayi_endRN','c:/temp/aa.fbx')