import os
import numpy as np
import torchvision.transforms as transforms
from torchvision.utils import save_image
from houseganapp_min.dataset.floorplan_dataset_maps_functional_high_res import FloorplanGraphDataset, floorplan_collate_fn
import torch
from houseganapp_min.models.models import Generator
from houseganapp_min.misc.utils import _init_input, draw_masks, draw_graph
from houseganapp_min.data.data import mytextpath
from Assets.Extraction.extraction import dump_path
from houseganapp_min.checkpoints.checkpoints import pretrained_path

def _infer(graph, model, prev_state=None):
    z, given_masks_in, given_nds, given_eds = _init_input(graph, prev_state)
    with torch.no_grad():
        masks = model(z.to('cpu'), given_masks_in.to('cpu'), given_nds.to('cpu'), given_eds.to('cpu'))
        masks = masks.detach().cpu().numpy()
    return masks

def generate(json_path):
    # create txt file containing the path to the json file
    with open(mytextpath, 'w') as f:
        f.write(json_path+'\n')

    model = Generator()
    model.load_state_dict(torch.load(pretrained_path, map_location=torch.device('cpu')), strict=True)
    model = model.eval()
    fp_dataset_test = FloorplanGraphDataset(mytextpath, transforms.Normalize(mean=[0.5], std=[0.5]), split='test')
    fp_loader = torch.utils.data.DataLoader(fp_dataset_test, 
                                            batch_size=1, 
                                            shuffle=False, collate_fn=floorplan_collate_fn)
    # optimizers
    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

    globalIndex = 0
    for i, sample in enumerate(fp_loader):
        # draw real graph and groundtruth
        mks, nds, eds, _, _ = sample
        real_nodes = np.where(nds.detach().cpu()==1)[-1]
        graph = [nds, eds]
        true_graph_obj, graph_im = draw_graph([real_nodes, eds.detach().cpu().numpy()])
        graph_im_path = os.path.join(dump_path, f'graph_{i}.png')
        graph_im.save(graph_im_path) # save graph

        # add room types incrementally
        _types = sorted(list(set(real_nodes)))
        selected_types = [_types[:k+1] for k in range(10)]
        _round = 0
        
        # initialize layout
        state = {'masks': None, 'fixed_nodes': []}
        masks = _infer(graph, model, state)
        im0 = draw_masks(masks.copy(), real_nodes)
        im0 = torch.tensor(np.array(im0).transpose((2, 0, 1)))/255.0 

        # generate per room type
        for _iter, _types in enumerate(selected_types):
            _fixed_nds = np.concatenate([np.where(real_nodes == _t)[0] for _t in _types]) \
                if len(_types) > 0 else np.array([]) 
            state = {'masks': masks, 'fixed_nodes': _fixed_nds}
            masks = _infer(graph, model, state)
            
        imk = draw_masks(masks.copy(), real_nodes)
        imk = torch.tensor(np.array(imk).transpose((2, 0, 1)))/255.0 
        # save locally on computer
        fp_im_path = os.path.join(dump_path, f'fp_{i}.png')
        save_image(imk, fp_im_path, format='PNG', nrow=1, normalize=False)