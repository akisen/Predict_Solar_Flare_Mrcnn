import pickle
import argparse
from tqdm import tqdm

def pickle_dump(obj, path):
    with open(path, mode='wb') as f:
        pickle.dump(obj, f)


def pickle_load(path):
    with open(path, mode='rb') as f:
        data = pickle.load(f)
        return data


# def vertical_flip_annotations(annotations):
#     annotations["segmentation"][0]
# return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pickle_path")
    args = parser.parse_args()
    pickle_path = args.pickle_path
    js = pickle_load(pickle_path)
    output_path=pickle_path.replace("val_pickle","test_pickle")
    for annotation in js["annotations"]:
        for i,ann in enumerate(annotation["segmentation"][0]):
            if i%2==0:
                ann =4102-ann
    pickle_dump(js,output_path)
main()
