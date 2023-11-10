**Dataset for Advance Driver Assistant Systems (ADAS)** is designed for object detection in Advanced Driver Assistance Systems, comprising 903 images and 1143 labeled objects across 9 classes like *pothole*, *left_hand_curve*, *right_hand_curve*, and other: *speed_breaker*, *bridge_ahead*, *pedestrian*, *animal*, *name_board*, and *vehicle*. The dataset covers diverse scenarios, including different road types, times of day, and capture angles. Notably, images were taken with two phone models, iPhone 12 and VIVO, ensuring variability for robust model evaluation.

Based on the exploration conducted, the author identified a shortage of datasets catering to solving Driver Assistant use cases, encompassing critical tasks like road sign detection, pedestrian detection, vehicle detection, animal detection, pothole detection, speed breaker detection, and more.

<img src="https://github.com/dataset-ninja/adas/assets/123257559/78188269-1b48-4051-a880-9fca20b921e9" alt="image" width="800">

Different scenarios that authors considered:
- Different type of roads (Highways, town roads, street/village roads)
- Different time (Darkness,Sunny, Rainy, Fog, crowded place and cloudy)
- Maintain distance/different angles to capture objects on the road.

<img src="https://github.com/dataset-ninja/adas/assets/123257559/50a86130-70ce-4fa8-ae4b-a4f05b175344" alt="image" width="800">

Also used 2 different configuration phones to capture images. (iphone 12 and VIVO)

<img src="https://github.com/dataset-ninja/adas/assets/123257559/ffbb7fee-8a32-460e-b90d-6579edf72b9a" alt="image" width="800">

Authors labelled data using the “labelme” tool. There are considered labels, across all categories:

- animal
- pedestrian
- name_board
- speed_beaker
- pothole
- right_hand_curve
- bridge_ahead
- left_hand_curve
