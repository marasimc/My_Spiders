class Config:
    model_def="config/yolov3-captcha.cfg"
    weights_path="checkpoints/yolov3_ckpt_pretrain.pth"
    class_path="data/captcha/classes.names"
    conf_thres=0.8
    nms_thres=0.4
    img_size=416