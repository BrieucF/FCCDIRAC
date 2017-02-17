#!/usr/bin/env python

#************************** libraries importation **************************#


#standard libraries

import getpass
import os
import glob
from os import listdir
from os.path import isfile, join
import re
from shutil import copyfile
import argparse


#DIRAC libraries

from DIRAC.Core.Workflow.Parameter import *
from DIRAC.Core.Workflow.Module import *
from DIRAC.Core.Workflow.Step import *
from DIRAC.Core.Workflow.Workflow import *
from DIRAC.Core.Workflow.WorkflowReader import *


#************************************* Classes - Definition ******************************#


class InstallationModule():
  


    #************************************#
    # Function name : write2file         #
    # input : file_name and its content  #
    # role : write the content in a file #
    #************************************#

    def write2file(self,operation,file_name,filetext):
        try:
            #create file with w permission  
            with open(file_name,operation) as text_file:
                text_file.write(filetext)
        except:
            print 'Error in writting file'
            quit()
            
    #********************************************************#
    # Function name : which                                  #
    # role : locate the sandbox on the worker node           #
    # and the DIRAC installation folder 'made on the fly'    #
    # by the pilotAgent                                      #
    # remark : the execution and installation modules        #
    # have different working directories !                   #
    #********************************************************#
             
    def which(self,file):
        for path in os.environ["PATH"].split(os.pathsep):
            if os.path.exists(os.path.join(path, file)):
                return os.path.join(path, file)
        return False
        
    #**********************************************************************************************************************************#
    # Function name : install_module                                                                                                   #
    # role : copy the execution module in                                                                                              #
    # the default path of DIRAC predefined modules : e.g.of a predefined Application and its corresponding module                      #
    # Marlin.py is located at -> ILCDIRAC/Interfaces/API/NewInterface/Applications/Marlin.py (Default predefined Applications folder)  #
    # MarlinAnalysis is located at -> ILCDIRAC/Workflow/Modules/MarlinAnalysis.py (Default predefined Modules folder)                  #
    #**********************************************************************************************************************************#
        
    def install_module(self):


        dirac_bins_path = self.which('dirac-wms-job-status')

        if False is dirac_bins_path:
            return False

        pilot_agent_cwd, tail = os.path.split(os.path.split(dirac_bins_path)[0])

        
        files = [f for f in listdir(pilot_agent_cwd)]

        #print '*****************************************************************************************************'
        #print '\n'.join(files)
        #print '*****************************************************************************************************'
        
        for f in files:
            #in the worker, the pilot agent put sandbox files in a 'JOB_ID' folder
            sandbox = re.match( r'\d+$', f, re.M|re.I)
            if None != sandbox:
                relative_sandbox = f
                absolute_sandox = pilot_agent_cwd + '/' + relative_sandbox
                
                #copy module
                copyfile(absolute_sandox + '/fcc_execution_module.py', pilot_agent_cwd + '/ILCDIRAC/Workflow/Modules/fcc_execution_module.py')
                #self.write2file('w',os.getcwd()+'/fsociety.dat',"LEAVE ME HERE")
                return True
                
                
    #****************************************************#
    # Function name : execute_module                     #
    # role : create the workflow of the execution module #
    #****************************************************#

    def execute_module(self,script_to_source,fcc_executable,fcc_conf_file,fcc_input_files,fcc_output_file,fccsw,number_of_events):


        
            
        #define FCC Module 
        fcc_module = ModuleDefinition('ExecutionModule')#during constraction class creates duplicating copies of the params
        fcc_module.setDescription('FCC module')
        fcc_module.setBody('from ILCDIRAC.Workflow.Modules.fcc_execution_module import ExecutionModule\n')

        fcc_module.addParameter(Parameter("script_to_source",script_to_source,"string","","",True,False,"The script to source"))        
        fcc_module.addParameter(Parameter("fcc_executable",fcc_executable,"string","","",True,False,"The executable you want to use ie. FCCSW,FCCPHYSICS..."))
        fcc_module.addParameter(Parameter("fcc_conf_file",fcc_conf_file,"string","","",True,False,"The configuration file you want to use."))
        fcc_module.addParameter(Parameter("fcc_input_files",fcc_input_files,"string","","",True,False,"The input files the job needs ie. --ifiles file1 file2 file3 ..."))
        fcc_module.addParameter(Parameter("fcc_output_file",fcc_output_file,"string","","",True,False,"The output file you want to create."))
        fcc_module.addParameter(Parameter("fccsw",fccsw,"string","","",True,False,"The use of fccsw software."))
        fcc_module.addParameter(Parameter("number_of_events",number_of_events,"string","","",True,False,"Number of events you want to generate"))
        
        fcc_step = StepDefinition('FCC_App_Step')
        fcc_step.addModule(fcc_module) # Creating instance of the module 'FCC_App_Step'
        fcc_module_instance = fcc_step.createModuleInstance('ExecutionModule', 'fcc_module')

        #fcc_step.addParameterLinked(fcc_module.parameters)


        fcc_workflow = Workflow(name='FCC Workflow')
        fcc_workflow.setDescription('Workflow of FCC Applications')

        fcc_workflow.addStep(fcc_step)
        fcc_step_instance = fcc_workflow.createStepInstance('FCC_App_Step', 'fcc')
        
        #fcc_step_instance.addParameter(Parameter("fcc_executable","","string","","",True,False,"first event number"))
        #fcc_step_instance.setValue("fcc_executable", fcc_executable)


        print fcc_workflow.createCode()

        fcc_workflow.execute()
    
    
#****************************************** Main ******************************************#

parser = argparse.ArgumentParser()

parser.add_argument("--source", action="store",dest="script_to_source",help="The script to source.")
parser.add_argument("--exec", "--executable", action="store",dest="fcc_executable",nargs='*',type=str,default="",help="The executable you want to use ie. FCCSW,FCCPHYSICS...")
parser.add_argument("--conf", action="store",dest="fcc_conf_file",help="The configuration file you want to use.")
parser.add_argument("--ifiles", action="store",dest="fcc_input_files",nargs='*',type=str,default="",help="The input files the job needs ie. --ifiles file1 file2 file3 ...")
parser.add_argument("--ofile", action="store",dest="fcc_output_file",default="",help="The output file you want to create.")
parser.add_argument("--fccsw", action="store",dest="fccsw",default="",help="The use of fccsw software.")
parser.add_argument("-N", action="store",dest="number_of_events", default="", help="Number of events you want to generate")
    
args = parser.parse_args()

script_to_source = args.script_to_source 
fcc_executable = args.fcc_executable
fcc_conf_file = args.fcc_conf_file
fcc_input_files = args.fcc_input_files
fcc_output_file = args.fcc_output_file
fccsw = args.fccsw
number_of_events = args.number_of_events
    
    
module = InstallationModule()    
is_installed = module.install_module()


#print '\n'.join(os.listdir(os.getcwd()))

#print 'EXECUTABLE'
#print fcc_executable

#print fccsw

if '' != fccsw :
    fcc_executable = ' '.join(fcc_executable[0:3]) + ' --xml ' + os.path.join(os.getcwd(),fcc_executable[3]) + ' ' + fcc_executable[4]  
else:
    fcc_executable = fcc_executable[0]
    
print 'EXECUTABLE'
print fcc_executable


if is_installed:
    module.execute_module(script_to_source,fcc_executable,fcc_conf_file,fcc_input_files,fcc_output_file,fccsw,number_of_events)
else:
    print 'DIRAC is not installed on this machine'

