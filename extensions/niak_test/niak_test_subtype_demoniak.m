function [pipeline,opt_pipe,files_in] = niak_test_subtype_demoniak(path_test,opt)
% Test the subtype pipeline on the preprocessed DEMONIAK dataset
%
% SYNTAX:
% [PIPELINE,OPT,FILES_IN] = NIAK_TEST_SUBTYPE_DEMONIAK(PATH_TEST,OPT)
%
% _________________________________________________________________________
% INPUTS:
%
% PATH_TEST.connectome (string) the path to the connectome output for the NIAK demo dataset.
% PATH_TEST.REFERENCE (string) the full path to a reference version of the 
%   results of the subtype pipeline. 
% PATH_TEST.RESULT (string) where to store the results of the test.
%
% OPT.EXT (string, default '.mnc.gz') the extension of imaging files.
% OPT.FLAG_TARGET (boolean, default false) if FLAG_TARGET == true, no comparison
%   with reference version of the results will be performed, but all test 
%   pipelines will still run. If this flag is used, PATH_TEST.REFERENCE
%   does not need to be specified.
% OPT.FLAG_TEST (boolean, default false) if FLAG_TEST == true, the demo will 
%   just generate the test PIPELINE.
% OPT.PSOM (structure) the options of the pipeline manager. See the OPT
%   argument of PSOM_RUN_PIPELINE. Note that the field PSOM.PATH_LOGS will be 
%   set up by the pipeline.
%
% _________________________________________________________________________
% OUTPUTS:
%
% PIPELINE (structure) a formal description of the test pipeline. 
%   See PSOM_RUN_PIPELINE.
% OPT_PIPE
%   (structure) the option to call NIAK_PIPELINE_SUBTYPE
% FILES_IN
%   (structure) the description of input files used to call 
%   NIAK_PIPELINE_SUBTYPE
%
% _________________________________________________________________________
% COMMENTS:
%
% The preprocessed DEMONIAK dataset can be found in multiple file formats at 
% the following address: http://www.nitrc.org/frs/?group_id=411
%
% This test will apply the subtype pipeline on the preprocessed DEMONIAK
% dataset, and will compare the outputs to a reference version of the
% results.
%
% It is possible to configure the pipeline manager to use parallel 
% computing using OPT.PSOM, see : 
% http://code.google.com/p/psom/wiki/PsomConfiguration
%
% Copyright (c) Pierre Bellec, Sebastian Urchs, Angela Tam
% Centre de recherche de l'institut de 
% Griatrie de Montral, Dpartement d'informatique et de recherche 
% oprationnelle, Universit de Montral, 2013.
% Maintainer : sebastian.urchs@mail.mcgill.ca
% See licensing information in the code.
% Keywords : test, NIAK, subtyping, pipeline, DEMONIAK

% Permission is hereby granted, free of charge, to any person obtaining a copy
% of this software and associated documentation files (the "Software"), to deal
% in the Software without restriction, including without limitation the rights
% to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
% copies of the Software, and to permit persons to whom the Software is
% furnished to do so, subject to the following conditions:
%
% The above copyright notice and this permission notice shall be included in
% all copies or substantial portions of the Software.
%
% THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
% IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
% FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
% AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
% LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
% OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
% THE SOFTWARE.

%% Check the input paths
path_test = psom_struct_defaults(path_test,{'connectome','reference','result'},{NaN,'',NaN});
if ~ischar(path_test.connectome)||~ischar(path_test.reference)||~ischar(path_test.result)
    error('PATH_TEST.{CONNECTOME,REFERENCE,RESULT} should be strings.')
end
path_test.connectome = niak_full_path(path_test.connectome);
path_test.reference  = niak_full_path(path_test.reference);
path_test.result     = niak_full_path(path_test.result);
path_logs = [path_test.result 'logs'];

%% Generate the subtype pipeline
if nargin < 2
    opt = struct();
end
opt = psom_struct_defaults(opt,{'ext','flag_target','flag_test','psom'},{'.mnc.gz',false,false,struct});
if strcmp(path_test.reference,'gb_niak_omitted')&&opt.flag_target
    error('Please specify PATH_TEST.REFERENCE')
end
opt_demo.folder_out = [path_test.result 'demoniak_subtype' filesep];
opt_demo.flag_test = true;
[pipeline,opt_pipe,files_in] = niak_demo_subtype(path_test.connectome,opt_demo);
list_jobs = fieldnames(pipeline);

%% Add a test: comparison of the result of the subtyping against the reference
if ~opt.flag_target
    clear in_c out_c opt_c
    in_c.source = {};
    in_c.target = {};
    out_c = [path_test.result 'report_test_regression_subtype_demoniak.csv'];
    opt_c.base_source = opt_demo.folder_out;
    opt_c.base_target = path_test.reference;
    opt_c.black_list_source = {[opt_demo.folder_out 'logs' filesep] ...
                               ,[opt_demo.folder_out 'networks' filesep 'aMPFC' filesep 'provenance_aMPFC.mat']};
    opt_c.black_list_target = {[path_test.reference 'logs' filesep] ...
                               ,[path_test.reference 'networks' filesep 'aMPFC' filesep 'provenance_aMPFC.mat']};
    pipeline = psom_add_job(pipeline,'test_subtype','niak_test_cmp_files',in_c,out_c,opt_c,false);
    pipeline.test_subtype.dep = list_jobs;
end

%% Run the pipeline
opt_pipe.psom = opt.psom;
opt_pipe.psom.path_logs = path_logs;
if ~isfield(opt,'flag_test')||~opt.flag_test
    psom_run_pipeline(pipeline,opt_pipe.psom);
end