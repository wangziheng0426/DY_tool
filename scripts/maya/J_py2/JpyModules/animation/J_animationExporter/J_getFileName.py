# -*- coding:utf-8 -*-
##  @package J_animationExporter
#
##  @brief   
##  @author 桔
##  @version 1.0
##  @date   12:03 2022/5/20
#  History:  

import maya.cmds as cmds
import maya.mel as mel
import re,os
import JpyModules
def J_getFileName():    
    fileName=cmds.file(query=True,sceneName=True,shortName=True)[:-3]
    fileName=re.search('(?i)ch\d*_s\d*[a-zA-Z]*_c\d*',fileName)
    if fileName!=None:
        return fileName.group()
    else:
        return ''
def J_analysisCamName():    
    fileFullName=cmds.file(query=True,sceneName=True)[:-3]
    #filePath=JpyModules.public.J_getMayaFileFolder()+'/cache'
    res=''
    jishu=re.search('/ss[0-9]{2}/',fileFullName)
    if jishu!=None:
        res= jishu.group()
    else:
        return ''
    
    juji=re.search('/ep[0-9]{2}/',fileFullName)
    if juji!=None:
        res=res+"_"+ juji.group()
    else:
        return ''
    
    changci=re.search('/s[0-9]{3}/',fileFullName)
    if changci!=None:
        res=res+"_"+ changci.group()
    else:
        return ''
    
    jingtou =re.search('/c[0-9]{4}/',fileFullName)
    if changci!=None:
        res=res+"_"+ jingtou.group()
    else:
        return ''
    
    return res.replace('/','')

#分析资产类型和名称，返回（类型_名称）
def J_analysisAssetsName(fileFullName):    
    #分析角色名，如果失败，则返回文件名
    if os.path.exists(fileFullName):
        chName=re.search('[a-zA-Z]*/\w*/rig/',fileFullName,re.IGNORECASE)
        if chName!=None:
            return chName.group().replace('/rig/','').replace('/','_')
        else:
            return os.path.splitext(os.path.basename(fileFullName))[0]
    else:
        print (u'文件不存在，请核实')
        return ('none_temp')
if __name__=='__main__':
    print J_analysisCamName()