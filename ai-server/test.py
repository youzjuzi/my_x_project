#yolov5
#导包
import torch
import cv2
from multiprocessing import Process, Manager, Value
#下面两个是yolov5文件夹里面的代码
from utils.general import non_max_suppression
from models.experimental import attempt_load

#确保在进行对象检测时，边界框的位置可以与输入图像的大小相对应，以便正确地识别和定位对象。
def scale_coords(img, coords, out_shape):
    # img: 输入图像，具有(C, H, W)的形状，表示通道数、高度和宽度。
    # coords: 包含边界框坐标的数组，具有(..., 4)的形状，其中...表示可变数量的维度，而最后一个维度4表示左上角和右下角的坐标。
    # out_shape: 输出尺寸，一个包含高度、宽度和通道数的元组或列表([out_h, out_w, _])。
    img_h, img_w = img.shape[2:]
    out_h, out_w, _ = out_shape
    coords[..., 0] *= out_w / img_w
    coords[..., 1] *= out_h / img_h
    coords[..., 2] *= out_w / img_w
    coords[..., 3] *= out_h / img_h
    # 通过按比例缩放坐标值来调整边界框的位置。首先，将输入图像的高度和宽度记录为img_h和img_w。
    # 然后，获取输出尺寸的高度和宽度，分别记录为out_h和out_w。
    # 接下来，通过计算比例因子out_w / img_w和out_h / img_h，将边界框的所有坐标值乘以相应的比例因子。
    # 这样做的目的是将坐标值映射到新的输出尺寸上，以便适应不同尺寸的输入图像。
    return coords
    #最后，返回经过缩放的坐标数组coords
def detect_objects(weights_path, output_frame):
    # 加载YOLOv5模型
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    #检查是否可用CUDA加速。如果CUDA可用，则将设备设置为'cuda'，否则设置为'cpu'。
    model = attempt_load(weights_path, device)

    # 设置置信度阈值和IoU阈值
    model.conf = 0.3
    model.iou = 0.5

    # 设置模型为推理模式
    model.eval()

    # 打开视频流
    cap = cv2.VideoCapture(0)
    cap.set(3, 640)  # 设置分辨率
    cap.set(4, 360)

    while True:
        ret, frame = cap.read()  # 视频读入
        if not ret:
            break

        # 图像预处理
        img = frame.copy()  # 创建一个副本以进行预处理
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = torch.from_numpy(img).to(device).float() / 255.0
        img = img.permute(2, 0, 1).unsqueeze(0)
        img = torch.nn.functional.interpolate(img, size=(320, 320), mode='bilinear', align_corners=False)
        # size = (320, 320)：表示目标输出图像的大小为320x320像素。将输入图像按照此大小进行调整。
        # mode = 'bilinear'：表示插值方法采用双线性插值。双线性插值是一种常用的插值方法，它通过对最近的四个像素进行加权平均来计算新像素值。
        # align_corners = False：表示在计算插值时不对齐角点。这个参数的具体影响取决于插值方法和具体的实现方式。
        # 进行物体检测
        outputs = model(img)
        results = non_max_suppression(outputs, conf_thres=model.conf, iou_thres=model.iou)
        # 通过非最大抑制算法对模型输出的边界框进行处理，以选择最佳的边界框并过滤掉冗余的检测结果。
        # outputs：模型的输出结果，通常是一个包含预测边界框及其置信度的数组。
        # conf_thres：表示置信度阈值，用于过滤掉置信度低于此阈值的边界框。
        # iou_thres：表示IoU（Intersection over Union）阈值，用于合并重叠度高于此阈值的边界框。
        #算法的步骤如下：
        # 1、根据置信度阈值过滤掉置信度低于阈值的边界框。
        # 2、对剩余的边界框按照置信度进行排序，置信度高的排在前面。
        # 3、从排好序的边界框列表中选择置信度最高的边界框，并将其添加到最终的结果列表中。
        # 4、遍历剩余的边界框列表，计算当前边界框与已选择的边界框的IoU值（重叠度），如果大于IoU阈值，则将其从列表中移除。
        # 5、重复步骤3和4，直到所有边界框都被处理完毕。
        # 6、最终，non_max_suppression()函数返回经过非最大抑制处理后的边界框结果。
        if results[0] is not None and len(results[0]) > 0:
            result = results[0]

        # 绘制边界框和标签
        for result in results:#逐个访问并获取
            if result is not None and len(result) > 0:
                result[:, :4] = scale_coords(img, result[:, :4], frame.shape).round()
                # result[:, :4]表示选取每个边界框的前四个元素，即边界框的坐标信息。
                for *xyxy, conf, cls in result:
                # result是一个数组或张量，每一行代表一个边界框，包含边界框的坐标、类别标签和置信度等信息。
                # *xyxy表示将边界框的前四个元素解包为一个名为xyxy的列表。这里的xyxy表示边界框的坐标信息，通常是左上角和右下角的坐标值。
                # conf表示边界框的置信度，通常是模型对该边界框所属类别的预测置信度。
                # cls表示边界框的类别标签，通常是模型对该边界框所属类别的预测结果。
                    label = f'{model.names[int(cls)]} {conf:.2f}'
                    # f'{model.names[int(cls)]} {conf:.2f}'使用了格式化字符串的语法，将类别名称和置信度转换为一个字符串。
                    # 其中，{model.names[int(cls)]}表示插入类别名称，
                    # {conf: .2f}表示插入置信度，并保留两位小数。
                    # 绘制边界框
                    xyxy = [int(x) for x in xyxy]
                    #将边界框的坐标值从浮点数转换为整数，以适应图像的像素值,将转换后的结果赋值给xyxy
                    cv2.rectangle(frame, (xyxy[0], xyxy[1]), (xyxy[2], xyxy[3]), (0, 255, 0), 2)
                    # 绘制标签
                    cv2.putText(frame, label, (xyxy[0], xyxy[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # 输出文本标签和坐标
                    print(label, xyxy)
                    global times
                    cent = (xyxy[2] - xyxy[0]) / 2 + xyxy[0]
                    if cent < frame.shape[1] / 3:  # 图像左侧
                        # print("LEFT")
                        pass
                    elif frame.shape[1] / 3 <= cent <= frame.shape[1] * 2 / 3:  # 图像中间
                        # print("Yes")
                        pass
                    elif cent > frame.shape[1] * 2 / 3:  # 图像右侧
                        # print("RIGHT")
                        pass

        cv2.imshow('frame', frame)
        #按q退出
        if cv2.waitKey(1) == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    # 设置权重文件路径
    weights_path = 'runs/yolov5s05/yolov5s052/weights/best.pt'

    # 使用 Manager 创建共享变量
    manager = Manager()
    output_frame = manager.dict()

    # 创建物体检测进程
    detection_process = Process(target=detect_objects, args=(weights_path, output_frame))
    detection_process.start()
    # 等待物体检测进程结束
    detection_process.join()


