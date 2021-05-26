""" Get Stats of Trajectory Categories """

import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('dataset_files', nargs='+',
                        help='Trajnet dataset file(s).')
    args = parser.parse_args()

    # for the case where a directory was supplied (remember that 'directory/*' where '*' is wildcard parameter, does
    # not work in Windows Operating System)
    if len(args.dataset_files) == 1 and os.path.isdir(args.dataset_files[0]):
        parent_dir = args.dataset_files[0]
        args.dataset_files = [os.path.join(parent_dir, file) for file in os.listdir(parent_dir)]

    total_tags, total_sub_tags = {1: [], 2: [], 3: [], 4: []}, {1: [], 2: [], 3: [], 4: []}

    for dataset_file in args.dataset_files:
        print('{dataset:>60s}'.format(dataset=dataset_file))
        tags = {1: [], 2: [], 3: [], 4: []}
        sub_tags = {1: [], 2: [], 3: [], 4: []}
        with open(dataset_file, 'r') as f:
            for line in f:
                line = json.loads(line)
                scene = line.get('scene')
                if scene is not None:
                    scene_id = scene['id']
                    scene_tag = scene['tag']
                    m_tag = scene_tag[0]
                    s_tag = scene_tag[1]
                    tags[m_tag].append(scene_id)
                    for s in s_tag:
                        sub_tags[s].append(scene_id)

        __print_stats__(tags, sub_tags)
        for i in range(1, 5):  # for each tag/subtag (same indexes); IF THE TAG NUMBERS CHANGE, THIS CODE MUST CHANGE
            # (the same applies to other regions of the code)
            total_tags[i].extend(tags[i])
            total_sub_tags[i].extend(sub_tags[i])

    print(f"{os.linesep}{os.linesep}ALL DATA")
    __print_stats__(total_tags, total_sub_tags)


def __print_stats__(tags, sub_tags):
    print("Total Scenes")
    print(len(tags[1]) + len(tags[2]) + len(tags[3]) + len(tags[4]))
    print("Main Tags")
    print("Type 1: ", len(tags[1]), "Type 2: ", len(tags[2]), "Type 3: ", len(tags[3]), "Type 4: ", len(tags[4]))
    print("Sub Tags")
    print("LF: ", len(sub_tags[1]), "CA: ", len(sub_tags[2]), "Group: ", len(sub_tags[3]), "Others: ", len(sub_tags[4]))


if __name__ == '__main__':
    main()
