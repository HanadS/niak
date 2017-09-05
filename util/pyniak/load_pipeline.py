__author__ = 'poquirion'

import shutil
import json
import os
import re
import subprocess
import tempfile
import logging

LOCAL_CONFIG_PATH = '/local_config'
PSOM_GB_LOCAL = "{}/../lib/psom_gb_vars_local.cbrain".format(os.path.dirname(os.path.realpath(__file__)))

try:
    import psutil
    psutil_loaded = True
except ImportError:
    psutil_loaded = False


def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def string(s):
    """
    :param s: A PSOM option
    :return: The right cast for octave
    """
    s.replace("\\", '')
    s = re.match("[\'\"]?([\w+\ -]*)[\'\"]?", s).groups()[0]
    if s in ['true', 'false', 'Inf']:
        return "{0}".format(s)
    return "'{0}'".format(s)


class BasePipeline(object):
    """
    This is the base class to run PSOM/NIAK pipeline under CBRAIN and the
    BOUTIQUE interface.
    """

    BOUTIQUE_PATH = "{0}/boutique_descriptor"\
        .format(os.path.dirname(os.path.realpath(__file__)))
    BOUTIQUE_INPUTS = "inputs"
    BOUTIQUE_CMD_LINE = "command-line-flag"
    BOUTIQUE_TYPE_CAST = {"Number": num, "String": string, "File": string, "Flag": string}
    BOUTIQUE_TYPE = "type"
    BOUTIQUE_LIST = "list"

    def __init__(self, pipeline_name, folder_in=None, folder_out=None, options=None, **kwargs):

        self.log = logging.getLogger(__file__)
        # literal file name in niak
        self.pipeline_name = pipeline_name

        # The name should be Provided in the derived class
        self._grabber_options = []
        self._pipeline_options = []

        # if os.path.islink(folder_in):
        #     self.folder_in = os.readlink(folder_in)
        # else:
        self.folder_in = folder_in
        self.folder_out = folder_out
        self.octave_options = options

        self.psom_gb_local_path = None

    def psom_gb_vars_local_setup(self):
        """
        This method is crucial to have psom/niak running properly on cbrain.
        :return:
        """
        self.psom_gb_local_path = "{0}/psom_gb_vars_local.m".format(LOCAL_CONFIG_PATH)
        shutil.copyfile(PSOM_GB_LOCAL, self.psom_gb_local_path)

    def run(self):
        self.log.debug("Run: {}".format(" ".join(self.octave_cmd)))
        p = None

        self.psom_gb_vars_local_setup()

        try:
            p = subprocess.Popen(self.octave_cmd)
            p.wait()
        except BaseException as e:
            if p and psutil_loaded:
                parent = psutil.Process(p.pid)
                try:
                    children = parent.children(recursive=True)
                except AttributeError:
                    children = parent.get_children(recursive=True)
                for child in children:
                    child.kill()
                parent.kill()
            logging.error("Could no process octave command")
            raise e

    @property
    def octave_cmd(self):
        tmp_oct = tempfile.NamedTemporaryFile('w', prefix='niak_script_', suffix='.m', dir='/tmp', delete=False)
        tmp_oct.write(("{0};\n{1}(files_in, opt);".format(";\n".join(self.octave_options), self.pipeline_name)))
        tmp_oct.close()
        return ["/usr/bin/env", "octave", "{}".format(tmp_oct.name)]

    @property
    def octave_options(self):

        opt_list = ["opt.folder_out=\'{0}\'".format(self.folder_out)]

        opt_list += self.grabber_construction()

        if self._pipeline_options:
            opt_list += self._pipeline_options

        return opt_list

    @octave_options.setter
    def octave_options(self, options):

        if options is not None:
            # Sort options between grabber (the input file reader) and typecast
            # them with the help of the boutique descriptor
            with open("{0}/{1}.json".format(self.BOUTIQUE_PATH, self.__class__.__name__)) as fp:
                boutique_descriptor = json.load(fp)

            casting_dico = {elem.get(self.BOUTIQUE_CMD_LINE, "")
                            .replace("--opt", "opt").replace("-", "."): [elem.get(self.BOUTIQUE_TYPE),
                                                                         elem.get(self.BOUTIQUE_LIST)]
                            for elem in boutique_descriptor[self.BOUTIQUE_INPUTS]}

            for optk, optv in options.items():


                optv = self.BOUTIQUE_TYPE_CAST[casting_dico[optk][0]](optv)

                # if casting_dico[boutique_opt][1] is True:

                if optk.startswith("--opt_g"):
                    self._grabber_options.append("{0}={1}".format(optk, optv))
                else:
                    self._pipeline_options.append("{0}={1}".format(optk, optv))



    def grabber_construction(self):
        """
        This method needs to be overload to fill the file_in requirement of NIAK
        :return: A list that contains octave string that fill init the file_in variable
        """
        pass



class FmriPreprocess(BasePipeline):

    def __init__(self, subjects=None, func_hint="", anat_hint="", *args,  **kwargs):
        super(FmriPreprocess, self).__init__("niak_pipeline_fmri_preprocess", *args, **kwargs)

        if subjects is not None:
            self.subjects = unroll_numbers(subjects)
        else:
            self.subjects = None
        self.func_hint = func_hint
        self.anat_hint = anat_hint

    def grabber_construction(self):
        """
        :return: A list that contains octave string that fill init the file_in variable

        """
        opt_list = []
        if os.path.isfile("{0}/{1}".format(os.getcwd(), self.folder_in)):
            in_full_path = "{0}/{1}".format(os.getcwd(), self.folder_in)
        else:
            in_full_path = "{0}".format(self.folder_in)
        list_in_dir = os.listdir(in_full_path)
        # TODO Control that with an option
        bids_description = None
        subject_input_list = None
        for f in list_in_dir:
            if f.endswith("dataset_description.json"):
                bid_path = "{0}/{1}".format(in_full_path, f)
                with open(bid_path) as fp:
                    bids_description = json.load(fp)
                break
            elif f.endswith("_demographics.txt"):
                subject_input_list = f
                break

        if subject_input_list:
            opt_list += ["list_subject=fcon_read_demog('{0}/{1}');".format(in_full_path, subject_input_list)]
            opt_list += ["opt_g.path_database='{0}/';".format(in_full_path)]
            opt_list += ["files_in=fcon_get_files(list_subject,opt_g);"]

        elif bids_description:
                opt_list += ["opt_gr = struct();"]
                if self.subjects:
                    logging.debug("subjects {}".format(self.subjects))
                    opt_list += ["opt_gr.subject_list = {0}".format(self.subjects).replace('[', '{').replace(']', '}')]
                if self.func_hint:
                    logging.debug("func hint {}".format(self.func_hint))
                    opt_list += ["opt_gr.func_hint = '{0}'".format(self.func_hint)]
                if self.anat_hint:
                    logging.debug("anat hint {}".format(self.anat_hint))
                    opt_list += ["opt_gr.anat_hint = '{0}'".format(self.func_hint)]

                opt_list += ["files_in=niak_grab_bids('{0}',opt_gr)".format(in_full_path)]

        else:

            # Todo find a good strategy to load subject, to is make it general! --> BIDS
            # % Structural scan
            opt_list += ["files_in.subject1.anat=\'{0}/anat_subject1.mnc.gz\'".format(self.folder_in)]
            # % fMRI run 1
            opt_list += ["files_in.subject1.fmri.session1.motor=\'{0}/func_motor_subject1.mnc.gz\'".format(self.folder_in)]
            opt_list += ["files_in.subject2.anat=\'{0}/anat_subject2.mnc.gz\'".format(self.folder_in)]
            # % fMRI run 1
            opt_list += ["files_in.subject2.fmri.session1.motor=\'{0}/func_motor_subject2.mnc.gz\'".format(self.folder_in)]

        return opt_list


class BASC(BasePipeline):
    """
    Class to run basc. Only work with outputs from niak preprocessing,
    at least for now.
    """

    def __init__(self, *args, **kwargs):
        super(BASC, self).__init__("niak_pipeline_stability_rest", *args, **kwargs)

    def grabber_construction(self):
        """
        :return:
        """
        file_in = []


        file_in.append("opt_g.min_nb_vol = {0}")
        file_in.append("opt_g.type_files = 'rest'")
        if self.subjects is not None and len(self.subjects) >= 1:
            file_in.append("opt_g.include_subject = {0}".format(self.subjects).replace('[', '{').replace(']', '}'))
        file_in.append("files_in = niak_grab_fmri_preprocess('{0}',opt_g)".format(self.folder_in))


        return file_in



# Set for supported class
SUPPORTED_PIPELINES = {"Niak_fmri_preprocess",
                       "Niak_basc",
                       "Niak_stability_rest"}


def suported(pipeline_name):

    if pipeline_name in SUPPORTED_PIPELINES:
        return True
    else:
        m = 'Pipeline {0} is not in not supported\nMust be part of {1}'.format(pipeline_name, SUPPORTED_PIPELINES)
        logging.warning(m)
        return False


def unroll_numbers(numbers):
    import re

    entries = [a[0].split('-') for a in  re.findall("([0-9]+((-[0-9]+)+)?)", numbers)]

    unrolled = []
    for elem in entries:
        if len(elem) == 1:
            unrolled.append(int(elem[0]))
        elif len(elem) == 2:
            unrolled += [a for a in range(int(elem[0]), int(elem[1])+1)]
        elif len(elem) == 3:
            unrolled += [a for a in range(int(elem[0]), int(elem[1])+1, int(elem[2]) )]

    return sorted(list(set(unrolled)))


if __name__ == '__main__':
    # folder_in = "/home/poquirion/test/data_test_niak_mnc1"
    # folder_out = "/var/tmp"
    #
    # basc = BASC(folder_in=folder_in, folder_out=folder_out)
    #
    # print(basc.octave_cmd)

    print(unroll_numbers("1,3,4 15-20, 44, 18-27-2"))
