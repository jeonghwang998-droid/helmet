import yaml

data = {'train' :  'C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/images',
        'val' :  'C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/images',
        'test' :  'C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/images',
        'nc': 2,
        'names': ['Without Helmet', 'With Helmet']
        }

# overwrite the data to the .yaml file
with open('C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/dataset.yaml', 'w') as f:
    yaml.dump(data, f)

# read the content in .yaml file
with open('C:/Users/82102/Desktop/yolo_test12/dl_workspace/dl_workspace/archive/working/dataset.yaml', 'r') as f:
    test_yaml = yaml.safe_load(f)
