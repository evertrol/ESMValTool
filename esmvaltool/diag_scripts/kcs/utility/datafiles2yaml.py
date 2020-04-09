import sys
import pathlib
import re
import pprint
import yaml


def reduce_ensembles(ensembles):
    ips = sorted(set([re.search(r'i\d+p\d+', ensemble).group() for ensemble in ensembles]))
    diff = {}
    ranges = []
    for ip in ips:
        temp = sorted(
            map(int,
                map(lambda x: x.group(1),
                    filter(None,
                           (re.search(fr'r(\d+){ip}', ensemble) for ensemble in ensembles)))))
        diff[ip] = [0] + [temp[i+1] - x for i, x in enumerate(temp[:-1])]
        start = end = -1
        for (ens, d, t) in zip(ensembles, diff[ip], temp):
            if start < 0:
                start = end = t
                continue
            if d > 1:
                if start == end:
                    ranges.append(fr'r{start}{ip}')
                else:
                    ranges.append(fr'r({start}:{end}){ip}')
                start = end = t
            else:
                end = t
        if start == end:
            ranges.append(fr'r{start}{ip}')
        else:
            ranges.append(fr'r({start}:{end}){ip}')
    return ranges


def test_reduce_ensembles():
    ensembles = ['r1i1p1', 'r1i1p2', 'r2i1p1', 'r3i1p1', 'r5i1p1', 'r4i1p1',
                 'r10i1p1', 'r9i1p1', 'r8i1p1', 'r12i1p1', 'r14i1p1', 'r16i1p1', 'r17i1p1']
    ensembles = reduce_ensembles(ensembles)
    assert ensembles == ['r(1:5)i1p1', 'r(8:10)i1p1', 'r12i1p1', 'r14i1p1', 'r(16:17)i1p1', 'r1i1p2']


def main():
    if sys.argv[1] == 'TEST':
        test_reduce_ensembles()
        return
    else:
        basedir = pathlib.Path(sys.argv[1])

    maxmodelstringlength = 0
    exps = ['historical', 'rcp26', 'rcp45', 'rcp60', 'rcp85']
    variables = ['tas', 'pr']
    datasets = []
    for exp in exps:
        if exp == 'historical':
            start, end = (1950, 2005)
        else:
            start, end = (2006, 2100)
        for var in variables:
            path = basedir / exp / 'Amon' / var
            models = path.glob('*')
            for model in models:
                if len(model.stem) > maxmodelstringlength:
                    maxmodelstringlength = len(model.stem)
                for ensemble in reduce_ensembles([p.stem for p in model.glob('r*')]):

                    datasets.append({'dataset': model.stem, 'project': 'CMIP5', 'exp': exp,
                                     'ensemble': ensemble, 'start_year': start, 'end_year': end})


    newdatasets = []
    for dataset in datasets:
        if dataset in newdatasets:
            continue
        newdatasets.append(dataset)
    datasets = newdatasets
    print("datasets:")
    keys = ['dataset', 'project', 'exp', 'ensemble', 'start_year', 'end_year']
    for dataset in datasets:
        #print(f"   - {{dataset: {dataset['dataset']:{maxmodelstringlength}}" + ", ".join([f"{key}: {dataset[key]}" for key in keys]) + "}")
        print("  - {" + ", ".join([f"{key}: {dataset[key]}" for key in keys]) + "}")
    #print(yaml.dump(datasets))
    return

if __name__ == '__main__':
    main()
