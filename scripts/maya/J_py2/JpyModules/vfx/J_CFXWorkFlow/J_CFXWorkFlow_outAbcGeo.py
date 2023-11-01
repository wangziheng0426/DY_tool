# -*- coding:utf-8 -*-
##  @package J_CFXWorkFlow_outAbcGeo
#
##  @brief  导出abc
##  @author 桔
##  @version 1.0
##  @date  16:46 2018/11/2
#  History:  废弃
##导出abc
import sys
import os,re
import shutil
import json
import maya.mel as mel
import maya.cmds as cmds
import maya.api.OpenMaya as om

def J_CFXWorkFlow_outAbcGeo():
    import JpyModules
    sel=cmds.ls(sl=1)
    if len(sel)<1:
        print (u"未选择要导出的对象")
        return
    #根据选择的对象进行查询，是否属于ref状态，如果是ref状态，则通过ref的文件确定缓冲目录和名称，否则使用名字空间作为名称
    for mitem in sel:
        outPath=JpyModules.public.J_getMayaFileFolder()+"/cache/"
        cacheName=''

        #判断是否为ref的对象
        if cmds.referenceQuery(mitem,isNodeReferenced=True):
            refNode=cmds.referenceQuery(mitem,tr=1,referenceNode=1)
            refFile=cmds.referenceQuery(refNode,filename=1)
            if os.path.exists(refFile):
                #新版根据meta解析资产并输出日志,如果存在meta，则使用meta的数据
                projName=os.path.basename(cmds.workspace(q=1,rd=1)[0:-1])
                asssetTypeName=''
                assetName=os.path.splitext(os.path.basename(refFile))[0]
                #找工程目录下的jmeta
                j_meta=JpyModules.pipeline.J_meta(cmds.workspace(q=1,rd=1)[0:-1])
                if len(j_meta.metaInfo)>0 :
                    if j_meta.metaInfo.has_key('baseInfo'):
                        if j_meta.metaInfo['baseInfo'].has_key('projectPath'):
                            projName=os.path.splitext(os.path.basename(j_meta.metaInfo['baseInfo']['projectPath']))[0]
                    if j_meta.metaInfo.has_key('userInfo'):
                        for uk,uv in j_meta.metaInfo['userInfo'].items():
                            if refFile.startswith(j_meta.metaInfo['baseInfo']['projectPath']+uv):
                                asssetTypeName=uv.split('/')[-1]
                                for ftItem in os.listdir(j_meta.metaInfo['baseInfo']['projectPath']+uv):
                                    if os.path.dirname(refFile).find(ftItem)>-1:
                                        assetName=ftItem
                #   print asssetTypeName
                if mitem.endswith('srfNUL'):
                    cacheName=projName+'_' +asssetTypeName+'_'+assetName+"_ani"
                elif mitem.endswith('simNUL'):
                    cacheName=projName+'_' +asssetTypeName+'_'+assetName+"_sim"
                else:
                    cacheName=projName+ asssetTypeName+"_"+mitem.replace(":","@")
                outPath+=asssetTypeName+'_'+assetName+"@"+refNode
        else:
            #如果选择的对象已经没有ref了，则通过节点名称分析，读取冒号前面的部分
            #解析项目名称            
            projName=os.path.basename(cmds.workspace(q=1,rd=1)[0:-1])
            outPath+=mitem.split(":")[0]
            cacheName=projName+'_'+mitem.replace(":","@")
        #如果是毛发曲线组，则输出曲线组的名称
        if mitem.find('_OutputCurves')>-1:
            cacheName=mitem.replace(":","@")
        print (u'输出缓存：'+outPath+"/"+cacheName)
        JpyModules.public.J_exportAbc(mode=0,exportMat=0,
                nodesToExport=[mitem],cacheFileName=cacheName,
                j_abcCachePath=outPath)
    os.startfile(JpyModules.public.J_getMayaFileFolder()+"/cache/")            
def J_CFXWorkFlow_selectSimGroup():
    cmds.select(cl=1)
    for item in cmds.ls(type="transform"):
        if item.endswith('srfNUL') or item.endswith('simNUL') or item.endswith('_OutputCurves') :
            cmds.select(item,tgl=1)
if __name__=='__main__':
    J_CFXWorkFlow_outAbcGeo()