import os.path
import subprocess
import json
import sys

"""
Testing JSON File

{
    "UUID": "00-333-322-OTI-NA-NE",
    "files": [
        {"name": "01-Sterea_1_video_00010_1_450k.mp4", "start": 0, "end": 10, "fade": 2},
        {"name": "Kyklades_B_Naxos_A_00002_1_450k.mp4", "start": 0, "end": 10, "fade": 2}
    ]
}
"""


def files_exists(files):
    """
    Checks if a file exists in the filesystem.
    :param files: String array of file names.
    :return: True if all files are found.
    """
    for index, file in enumerate(files):
        if os.path.isfile(file):
            print("File found {}".format(file))
        else:
            print("Files {} not found!".format(file))
            return False
    return True


def insert_root_path(files, files_root):
    """
    Inserts a root path in front of the files array.
    :param files_root: The root folder there the video are locates in the system.
    :param files: String array of file names.
    """
    for i, f in enumerate(files):
        files[i]['name'] = files_root + '/' + f['name']


def create_directory(path):
    """
    Creates a directory or directories (mkdir -p).
    :param path: The directory path to be created.
    """
    if not os.path.exists(path):
        os.makedirs(path)


def cut_fade_video(input_video, output_name, start, end, fade_duration):
    """
    This method creates a new video file that is cut and put fade in and out effect from
    the original video using ffmpeg.
    
    :param input_video: The input video file name.
    :param output_name: The output path of the result.
    :param start: The start of the video.
    :param end: The end of the video.
    :param fade_duration: The fade in/out duration.
    :return: The output file name.
    """
    shit = r"fade=in:st={}:d={},fade=out:st={}:d={}".format(
        start,
        fade_duration,
        end - fade_duration,
        fade_duration)
    subprocess.call(['ffmpeg',
                     '-i', input_video,
                     '-vf', shit,
                     '-ss', str(start),
                     '-to', str(end),
                     '-an', output_name, '-y'])

    return output_name


def create_sub_video_files_txt(postfix, root_folder):
    """
    Creates a list.txt with the intermediate file names.
    :param root_folder: The root folder of the order.
    :param postfix: The postfix of the intermediate files.
    :return: The list file name.
    """
    output_path = os.path.join(root_folder, 'list.txt')
    with open(output_path, 'w+') as list_file:
        for file in os.listdir(root_folder):
            if file.endswith(postfix):
                list_file.write('file \'{}\''.format(file))
                list_file.write('\n')
    return output_path


def merge_video_files(postfix, root_folder):
    """
    Merges the cut video files into one.
    :param postfix: The postfix of the sub video files.
    :param root_folder: The root folder of the order.
    """
    sub_video_file_name = create_sub_video_files_txt(postfix, root_folder)
    video_result_path = os.path.join(root_folder, 'result.mp4')
    subprocess.call(['ffmpeg',
                     '-f', 'concat',
                     '-i', sub_video_file_name,
                     '-c', 'copy',
                     '-an', video_result_path, '-y'])


def annotate_done(order_output_folder):
    """
    Creates an empty file named 'DONE' to indicate that the process is complete.
    :param order_output_folder: The output folder of the order.
    """
    open(os.path.join(order_output_folder, 'DONE'), 'w')


def start_processing(json_data, defaults):
    """
    Main body of the functionality.
    Creates the sub video cut and faded. Then it merges them in one video file.
    All the generated videos are put in a folder designated by the UUID of the order.
    When the 'DONE' file in the order is present the process is complete.
    :param json_data: See sample json file and the top of this file.
    :param defaults: The default vars (just the source folder for now)
    """

    data = json.load(json_data)
    insert_root_path(data['files'], defaults['source_files'])
    order_output_folder = data['UUID']
    create_directory(order_output_folder)
    output_postfix = '.intermediate.mp4'

    for index, file in enumerate(data['files']):
        output_file_name = os.path.join(order_output_folder, str(index) + output_postfix)
        cut_fade_video(file['name'], output_file_name, file['start'], file['end'], file['fade'])

    merge_video_files(output_postfix, order_output_folder)
    annotate_done(order_output_folder)


# Testing main
if __name__ == "__main__":
    start_processing(sys.stdin, {'source_files': '/Users/nikolas/Desktop/test/'})
