import shutil
import optparse
from os import listdir, mkdir
from os.path import abspath, join, exists
from codecs import open
from lxml import etree
from math import floor

def voc2yolo(output_p, imgs_p, labels_p, split_ratios = None):
    img_filetype = ['.jpg',  '.jpeg', '.png', '.tiff', '.tif']
    classes_name = {} # store unique class name {class_name:0}
    yolo_labels = {} # {file_name:file_content}
    xmlFiles = list(filter(lambda x: x.endswith('.xml'), listdir(labels_p)))
    n_imgs = len(xmlFiles)
    counter = 0
    for xmlFile in xmlFiles:
        trees = etree.parse(labels_p + '/' + xmlFile)
        width, height = int(trees.find('size/width').text), int(trees.find('size/height').text)
        yolo_labels[xmlFile[:-4]] = ''
        for obj in trees.findall('object'):
            bdb = obj.find('bndbox')
            name = obj.find('name').text
            xmin = int(bdb.find('xmin').text)
            ymin = int(bdb.find('ymin').text)
            xmax = int(bdb.find('xmax').text)
            ymax = int(bdb.find('ymax').text)
            center_x = (xmin + (xmax-xmin)/2)/width
            center_y = (ymin + (ymax-ymin)/2)/height
            bdb_w = (xmax-xmin)/width
            bdb_h = (ymax-ymin)/height
            if name not in classes_name.keys():
                classes_name[name] = len(classes_name)
            yolo_labels[xmlFile[:-4]] += '{} {:6f} {:6f} {:6f} {:6f}\n'.format(
                    classes_name[name], center_x, center_y, bdb_w, bdb_h)
    if split_ratios == None:
        for filename in yolo_labels:
            save_path = join(output_p, 'labels')
            open(join(save_path, filename+'.txt'), 'w', encoding='utf-8-sig').write(yolo_labels[filename])
            for ft in img_filetype:
                src = join(imgs_p, f'{filename}{ft}')
                dst = join(output_p, f'images/{filename}{ft}')
                if exists(src):
                    shutil.copy(src, dst)
                    break
    else:
        n_train = floor(n_imgs*(split_ratios[0]/10))
        n_val = round(n_train*(split_ratios[2]/10))
        for filename in yolo_labels:
            if counter < n_train:
                if counter < n_train - n_val:
                    split_to = 'train'
                else:
                    split_to = 'val'
            else:
                split_to = 'test'
            save_path = join(output_p, f'labels/{split_to}')
            open(join(save_path, f'{filename}.txt'), 'w', encoding='utf-8-sig').write(yolo_labels[filename])
            for ft in img_filetype:
                src = join(imgs_p, f'{filename}{ft}')
                dst = join(output_p, f'images/{split_to}/{filename}{ft}')
                if exists(src):
                    shutil.copy(src, dst)
                    break
            counter += 1
    with open(f'{output_p}/dataset_meta.txt', 'w', encoding='utf-8-sig') as f:
        content = 'Class Name\tID\n'
        for class_name in classes_name:
            content += f'{class_name}\t{classes_name[class_name]}\n'
        if split_ratios != None:
            content += f'Number of Training Set : {floor(n_imgs*(split_ratios[0]/10))-round(floor(n_imgs*(split_ratios[0]/10))*(split_ratios[2]/10))}\nNumber of Testing Set : {counter-floor((n_imgs*(split_ratios[0]/10)))}\nNumber of Validation Set : {round(floor(n_imgs*(split_ratios[0]/10))*(split_ratios[2]/10))}'
        else:
            content += f'Number of Dataset : {n_imgs}'
        f.write(content)
    print('Convert completed!')

option_list = [
        optparse.make_option('-o', '--output-path', help='Relative path to directory that used to store converted result.', type='string', dest='outpath'),
        optparse.make_option('-i', '--imgs-path', help='Relative path to directory that contains PascalVoc images', type='string', dest='imgspath'),
        optparse.make_option('-l', '--labels-path', help='Relative path to directory that contains PascalVoc labels', type='string', dest='labelspath'),
        optparse.make_option('-t', '--ttv', help='Train Test Validation ratio, seperate each ratio with comma(,) e.g. 8,2,2 is mean 80% of the dataset is split into training set, 20% is split into testing set and 20% of training set is split into validation set', type='string', dest='ttv', default='8,8,2'),
        optparse.make_option('-s', '--split', help='Split dataset into train, test and validation, input as boolean', type='string', dest='split', default='false')
    ]
parser = optparse.OptionParser(option_list=option_list)

if __name__ == "__main__":
    curr_path = abspath('.')
    opts, args = parser.parse_args()
    imgs_path = join(curr_path, abspath(opts.imgspath))
    labels_path = join(curr_path, abspath(opts.labelspath))
    if exists(imgs_path) and exists(labels_path):
        if not exists(join(curr_path, abspath(opts.outpath))):
            out_path = join(curr_path, abspath(opts.outpath))
            out_imgs_path = join(out_path, 'images')
            out_labels_path = join(out_path, 'labels')
            mkdir(out_path)
            mkdir(out_imgs_path)
            mkdir(out_labels_path)
            if opts.split in ['true', 'True', '1', 'yes']:
                mkdir(join(out_imgs_path, 'train'))
                mkdir(join(out_imgs_path, 'test'))
                mkdir(join(out_imgs_path, 'val'))
                mkdir(join(out_labels_path, 'train'))
                mkdir(join(out_labels_path, 'test'))
                mkdir(join(out_labels_path, 'val'))
                split_ratios = (opts.ttv).split(',')
                if len(split_ratios) != 3:
                    split_ratios = (8, 8, 2)
                if all(list(map(lambda x: x in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'], split_ratios))):
                    try:
                        if int(split_ratios[0])+int(split_ratios[1]) != 10:
                            split_ratios = (8, 8, 2)
                        if int(split_ratios[2]) == int(split_ratios[0]): # Has no training set
                            split_ratios = (8, 8, 2)
                        split_ratios = (int(split_ratios[0]), int(split_ratios[1]), int(split_ratios[2]))
                    except:
                        split_ratios = (8, 8, 2)
                else:
                    split_ratios = (8, 8, 2)
                voc2yolo(out_path, imgs_path, labels_path, split_ratios)
            else:
                voc2yolo(out_path, imgs_path, labels_path)
    else:
        print('Please correct -i and -l')
