import supervisely as sly
import os, glob
from dataset_tools.convert import unpack_if_archive
import src.settings as s
from urllib.parse import unquote, urlparse
from supervisely.io.fs import get_file_name, get_file_ext, file_exists
from supervisely.io.json import load_json_file
import shutil


from tqdm import tqdm

def download_dataset(teamfiles_dir: str) -> str:
    """Use it for large datasets to convert them on the instance"""
    api = sly.Api.from_env()
    team_id = sly.env.team_id()
    storage_dir = sly.app.get_data_dir()

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, str):
        parsed_url = urlparse(s.DOWNLOAD_ORIGINAL_URL)
        file_name_with_ext = os.path.basename(parsed_url.path)
        file_name_with_ext = unquote(file_name_with_ext)

        sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
        local_path = os.path.join(storage_dir, file_name_with_ext)
        teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

        fsize = api.file.get_directory_size(team_id, teamfiles_dir)
        with tqdm(
            desc=f"Downloading '{file_name_with_ext}' to buffer...",
            total=fsize,
            unit="B",
            unit_scale=True,
        ) as pbar:        
            api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)
        dataset_path = unpack_if_archive(local_path)

    if isinstance(s.DOWNLOAD_ORIGINAL_URL, dict):
        for file_name_with_ext, url in s.DOWNLOAD_ORIGINAL_URL.items():
            local_path = os.path.join(storage_dir, file_name_with_ext)
            teamfiles_path = os.path.join(teamfiles_dir, file_name_with_ext)

            if not os.path.exists(get_file_name(local_path)):
                fsize = api.file.get_directory_size(team_id, teamfiles_dir)
                with tqdm(
                    desc=f"Downloading '{file_name_with_ext}' to buffer...",
                    total=fsize,
                    unit="B",
                    unit_scale=True,
                ) as pbar:
                    api.file.download(team_id, teamfiles_path, local_path, progress_cb=pbar)

                sly.logger.info(f"Start unpacking archive '{file_name_with_ext}'...")
                unpack_if_archive(local_path)
            else:
                sly.logger.info(
                    f"Archive '{file_name_with_ext}' was already unpacked to '{os.path.join(storage_dir, get_file_name(file_name_with_ext))}'. Skipping..."
                )

        dataset_path = storage_dir
    return dataset_path
    
def count_files(path, extension):
    count = 0
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(extension):
                count += 1
    return count
    
def convert_and_upload_supervisely_project(
    api: sly.Api, workspace_id: int, project_name: str
) -> sly.ProjectInfo:
    dataset_path = "ADAS"
    batch_size = 30
    images_ext = ".jpg"
    ann_ext = ".json"
    ds_name = "ds"

    imgs = []

    for r, d, f in os.walk(dataset_path):
        for file in f:
            if get_file_ext(file) == images_ext:
                if file in imgs:
                    '''jpg'''
                    old_path = os.path.join(r, file)
                    path, _ = os.path.split(r)
                    new_name = os.path.basename(path) + '_' + file
                    new_path = os.path.join(r, new_name)
                    os.rename(old_path, new_path)
                    '''ann'''
                    filename = get_file_name(file)
                    ann_name = filename + ann_ext
                    old_path_ann = os.path.join(r, ann_name)
                    new_ann_name = os.path.basename(path) + '_' + ann_name
                    new_path_ann = os.path.join(r, new_ann_name)
                    os.rename(old_path_ann, new_path_ann)
                else:
                    imgs.append(file)

    def create_ann(image_path):
        labels = []
        tags = []

        ann_path = image_path.replace(images_ext, ann_ext)

        path2img, _ = os.path.split(image_path)
        path2id, subfolder_value = os.path.split(path2img)
        path2cat, cat_dir = os.path.split(path2id)
        if cat_dir in ["normal roads", "village_raods"]:
            road_value = cat_dir
            path2cat, cat_dir = os.path.split(path2cat)
            road = sly.Tag(road_meta, value=road_value)
            tags.append(road)
        cat = sly.Tag(cat_meta, value=cat_dir)
        tags.append(cat)
        _ , camera_value = os.path.split(path2cat)
        camera = sly.Tag(camera_meta, value=camera_value)
        tags.append(camera)
        subfolder = sly.Tag(subfolder_meta, value=subfolder_value)
        tags.append(subfolder)

        if file_exists(ann_path):
            ann_data = load_json_file(ann_path)
            img_height = ann_data["imageHeight"]
            img_wight = ann_data["imageWidth"]

            for curr_data in ann_data["shapes"]:
                obj_class = name_to_class[curr_data["label"]]
                points = curr_data["points"]
                left = int(points[0][0])
                right = int(points[1][0])
                top = int(points[0][1])
                bottom = int(points[1][1])
                if top > bottom:
                    top = int(points[1][1])
                    bottom = int(points[0][1])
                if left > right:
                    left = int(points[1][0])
                    right = int(points[0][0])
                rectangle = sly.Rectangle(top=top, left=left, bottom=bottom, right=right)
                label = sly.Label(rectangle, obj_class)
                labels.append(label)

        else:
            image_np = sly.imaging.image.read(image_path)[:, :, 0]
            img_height = image_np.shape[0]
            img_wight = image_np.shape[1]

        return sly.Annotation(img_size=(img_height, img_wight), labels=labels, img_tags=tags)


    animal = sly.ObjClass("animal", sly.Rectangle)
    pedestrian = sly.ObjClass("pedestrian", sly.Rectangle)
    name_board = sly.ObjClass("name_board", sly.Rectangle)
    speed_breaker = sly.ObjClass("speed_breaker", sly.Rectangle)
    pothole = sly.ObjClass("pothole", sly.Rectangle)
    right_hand_curve = sly.ObjClass("right_hand_curve", sly.Rectangle)
    bridge_ahead = sly.ObjClass("bridge_ahead", sly.Rectangle)
    left_hand_curve = sly.ObjClass("left_hand_curve", sly.Rectangle)
    vehicle = sly.ObjClass("vehicle", sly.Rectangle)


    name_to_class = {
        "vehicle": vehicle,
        "animal": animal,
        "pedestrian": pedestrian,
        "name_board": name_board,
        "speed_breaker": speed_breaker,
        "pothole": pothole,
        "right_hand_curve": right_hand_curve,
        "bridge_ahead": bridge_ahead,
        "left_hand_curve": left_hand_curve,
    }

    subfolder_meta = sly.TagMeta("id", sly.TagValueType.ANY_STRING)
    cat_meta = sly.TagMeta("category", sly.TagValueType.ANY_STRING)
    camera_meta = sly.TagMeta("camera", sly.TagValueType.ANY_STRING)
    road_meta = sly.TagMeta("road_type", sly.TagValueType.ANY_STRING)

    project = api.project.create(workspace_id, project_name, change_name_if_conflict=True)
    meta = sly.ProjectMeta(
        obj_classes=list(name_to_class.values()), tag_metas=[subfolder_meta, camera_meta, road_meta, cat_meta]
    )
    api.project.update_meta(project.id, meta.to_json())

    dataset = api.dataset.create(project.id, ds_name, change_name_if_conflict=True)

    images_pathes = glob.glob(dataset_path + "/*/*/*/*/*.jpg") + glob.glob(
        dataset_path + "/*/*/*/*/*/*.jpg"
    )

    progress = sly.Progress("Create dataset {}".format(ds_name), len(images_pathes))

    for img_pathes_batch in sly.batched(images_pathes, batch_size=batch_size):
        img_names_batch = [os.path.basename(path) for path in img_pathes_batch]
        # for im_path in img_pathes_batch:
        #     im_name = get_file_name_with_ext(im_path)
        #     if im_name not in not_unique_names:
        #         img_names_batch.append(im_name)
        #     else:
        #         img_names_batch.append(im_path.split("/")[-3] + "_" + im_name)

        img_infos = api.image.upload_paths(dataset.id, img_names_batch, img_pathes_batch)
        img_ids = [im_info.id for im_info in img_infos]

        anns = [create_ann(image_path) for image_path in img_pathes_batch]
        api.annotation.upload_anns(img_ids, anns)

        progress.iters_done_report(len(img_names_batch))

    return project
