import re
import pandas as pd
from pathlib import Path

class DendroImageManager():

    @staticmethod
    def get_metadata_by_sample(sample_dir: str, subsample_dir: str, accepted_formats: list[str]) -> dict:
        # Load metadata from both folders
        df = pd.DataFrame([dendroimage for dendroimage in DendroImageManager._get_metadata_from_dirs(sample_dir, subsample_dir, accepted_formats)])
        if len(df) == 0:
            return {}
        
        # Setting dtype manually
        df['site'] = df['site'].map(lambda val: str(val) if val else None)
        df['species'] = df['species'].map(lambda val: str(val) if val else None)
        df['tree'] = df['tree'].map(lambda val: str(val) if val else None)
        df['sample'] = df['sample'].map(lambda val: int(val) if val else -1)
        df['subsample'] = df['subsample'].map(lambda val: int(val) if val else -1)
        df['extras'] = df['extras'].map(lambda val: str(val) if val else None)
        df['file'] = df['file'].map(lambda val: str(val) if val else None)
        df['path'] = df['path'].map(lambda val: str(val) if val else None)
        
        # Sort and group
        df.sort_values(['site', 'tree', 'sample', 'subsample', 'extras'], 
               axis = 0,
               ascending = True,
               inplace = True,
               na_position = "first")
        df_by_sample = df.groupby(['site', 'tree', 'sample'])
        
        # Extract relevant records (sample preview, annotated twin subsamples and default subsamples as backup)
        metadata_by_sample = {}
        for sample, group_data in df_by_sample:
            group_data = group_data.drop_duplicates()
            metadata_by_sample[sample] = {
                "preview": None,
            }
            sample_preview = group_data[(group_data.extras == 'PREVIEW') & (group_data.subsample < 0)]
            subsamples_annotated_twin = group_data[(group_data.extras == 'ANNOTATED_TWIN') & (group_data.subsample >= 0)]
            subsamples_default = group_data[(group_data.extras.isnull()) & (group_data.subsample >= 0)]
            if len(sample_preview) > 0:
                metadata_by_sample[sample].update({
                    "preview": sample_preview.iloc[0].to_dict()
                })
            metadata_by_sample[sample].update({
                "subsamples_annotated_twin": {rec['subsample']: rec for rec in subsamples_annotated_twin.to_dict(orient='records')},
                "subsamples_default": {rec['subsample']: rec for rec in subsamples_default.to_dict(orient='records')}
            })
        # metadata_by_sample = {sample: group_data.drop_duplicates().to_dict(orient='records') for sample, group_data in df_by_sample}
        # print(metadata_by_sample)
        return metadata_by_sample

    @staticmethod
    def _get_metadata_from_dirs(sample_dir: str, subsample_dir: str, accepted_formats: list[str]) -> list[dict]:
        return DendroImageManager._get_metadata_in_dir(Path(sample_dir), accepted_formats) + \
            DendroImageManager._get_metadata_in_dir(Path(subsample_dir), accepted_formats)

    @staticmethod
    def _get_metadata_in_dir(work_dir: Path, accepted_formats: list[str]) -> list[dict]:
        images = []
        for file in work_dir.iterdir():
            *image_name, format = tuple(file.name.split("."))
            
            # Ignore unaccepted file formats
            if not file.is_file() or format not in accepted_formats:
                continue
            
            # Parse file name to extract fields of interest
            image_attributes = DendroImageManager._parse_filename_to_attributes(file.name, file.absolute())
            if not image_attributes or any([image_attributes.get(mand_key) is None for mand_key in ["site", "tree", "sample"]]):
                continue

            images.append(image_attributes)
        return images

    @staticmethod
    def _parse_filename_to_attributes(filename: str, path: str) -> dict:
        if filename.startswith("."):
            return None
        
        *name, ext = filename.split(".")
        name = '.'.join(name)
        
        # Extract image name parts starting from the end, in the order Extras, [Subsample], Sample, [Species], Tree, Site

        # Extract extras
        m = re.match("^.*_[0-9]+", name)
        if m:
            m_idx = m.span()[1]
            name, extra = name[:m_idx].strip("_"), name[m_idx:].strip("_")
        
        # Extract Sample/Subsample numbers (also extracts Tree if this is numeric)
        sample, subsample = None, None
        numbers = []
        while name:
            m = re.match("^.*_([0-9]+)$", name)
            if m:
                number = m.group(1)
                name = name[:len(name) - len(number)].strip("_")
                numbers.append(number)
            else:
                break
        
        species = None
        tree = None
        m = re.match("(^.*)_([A-Z]{4})(.*)$", name)
        if m: # Try to extract Tree if species present
            species = m.group(2)
            if len(m.group(3)) > 0:
                tree = m.group(3).strip("_")
            name = m.group(1)
        else: # Try to extract Tree if species missing (everything after first "_")
            m = re.match("^[^_]*_(.*)$", name)
            if m:
                tree = m.group(1).strip("_")
                name = name[:len(name) - len(tree)].strip("_")
        
        # Tree may have already been extracted into the numbers list
        if tree is None:
            tree = numbers.pop()
        
        if len(numbers) not in [1, 2]:
            return None

        if len(numbers) == 2:
            subsample, sample  = tuple(numbers)
        else:
            sample = numbers.pop()

        # Characters remaining in name are the site
        site = name

        # print(file, site, tree, sample, subsample, extra, ext)
        
        image_attr = {
            "site": site, 
            "species": species, 
            "tree": tree, 
            "sample": sample, 
            "subsample": subsample, 
            "extras": extra.upper() if len(extra) else None,
            "file": filename,
            "path": path
        }
        # print(filename, image_attr)
        return image_attr