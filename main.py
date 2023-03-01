import os
import sys
import time

import matplotlib.pyplot as plt
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.uic.properties import QtGui
from keras.preprocessing.image import ImageDataGenerator
from keras.utils import load_img, img_to_array, array_to_img
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# ui 불러오기
form_class = uic.loadUiType("ui/main.ui")[0]
generating_class = uic.loadUiType("ui/generating.ui")[0]
howtohelp_class = uic.loadUiType("ui/howtohelp.ui")[0]
optionhelp_class = uic.loadUiType("ui/optionhelp.ui")[0]


# 윈도우 클래스, ui파일 전달
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 클래스 내에서 여러 함수들에 사용할 변수
        self.file = None  # 파일 1개 정보 저장하는 변수
        self.folder = None  # 폴더의 경로 저장하는 변수
        self.files_root = []  # 파일들의 경로 저장되어 있는 리스트

        # 원하는 레이아웃에 matplotlib를 연동되게 해주는 부분 미리 세팅
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        self.plt_layout.addWidget(self.canvas)

        # 이벤트 모음
        self.fileOpen_action.triggered.connect(self.fileOpne)  # 파일 열기 클릭 이벤트
        self.directoryOpen_action.triggered.connect(self.dirOpen)  # 경로 열기 클릭 이벤트
        self.preview_button.clicked.connect(self.preview)  # 미리보기 버튼 클릭 이벤트
        self.generateAndSave_action.triggered.connect(self.generateAndSave)  # 저장하기 클릭 아밴트
        self.generateAndSave_button.clicked.connect(self.generateAndSave)  # 만들고 저장하기 버튼 클릭 이벤트
        self.optionHelp_action.triggered.connect(self.openOptionHelp)  # 속성 도움말 클릭 이벤트
        self.howtoHelp_action.triggered.connect(self.openHowToHelp)  # 사용법 도움말 클릭 이벤트

    def fileOpne(self):
        # 파일 열기 창을 열리게 해줌
        self.file = QFileDialog.getOpenFileName(self, '', '', 'Image(*.bmp *.jpg *.png)')

        # 만약 파일이 열렸다면(취소 버튼 안누름)
        if bool(self.file[0]):
            # 이전 파일 초기화
            self.files_root = []

            # 튜플 형식의 변수에서 파일명만 따서 저장
            self.files_root.append(self.file[0])

            # 이제 미리보기와 이미지 만들고 저장하는 기능 이용하도록 버튼 활성화
            self.preview_button.setEnabled(True)
            self.generateAndSave_button.setEnabled(True)

    def dirOpen(self):
        # 폴더 선택 창을 열리게 해줌
        self.folder = QFileDialog.getExistingDirectory(self)

        if bool(self.folder):
            # 만약 폴더를 선택한다면 이전 결과물 초기화
            self.files_root = []

            # 파일들을 다 저장하되 이미지 파일만 저장
            for (root, directories, files) in os.walk(self.folder):
                for file in files:
                    file_path = os.path.join(root, file)  # file_path 변수에 파일 경로 1개 불러옴
                    # 이미지 확장자에 포함되는경우(이미지파일만 걸러냄)
                    if os.path.splitext(file_path)[1] == '.jpg' or os.path.splitext(file_path)[1] == '.png' or \
                            os.path.splitext(file_path)[1] == '.bmp':
                        self.files_root.append(file_path)  # files_root에 이미지 경로 1개 추가

            if self.files_root:
                # 이제 미리보기와 이미지 만들고 저장하는 기능 이용하도록 버튼 활성화
                self.preview_button.setEnabled(True)
                self.generateAndSave_button.setEnabled(True)

    def preview(self):
        # 제너레이터에 넣을 속성값 프로그램에서 가져오기
        horizontalFlip = self.horizontalFlip_comboBox.currentText() == 'True'
        widthShiftRange = self.widthShiftRange_SpinBox.value()
        heightShiftRange = self.heightShiftRange_spinBox.value()
        rotationRange = self.rotationRange_spinBox.value()
        shearRange = self.shearRange_spinBox.value()
        zoomRange = self.zoomRange_spinBox.value()
        verticalFlip = self.verticalFlip_comboBox.currentText() == 'True'
        fillMode = self.fillMode_comboBox.currentText()

        # 사용자 속성에 맞춘 이미지 제너레이터 준비
        datagen = ImageDataGenerator(horizontal_flip=horizontalFlip, width_shift_range=widthShiftRange,
                                     height_shift_range=heightShiftRange, rotation_range=rotationRange,
                                     shear_range=shearRange, zoom_range=zoomRange,
                                     vertical_flip=verticalFlip, fill_mode=fillMode)

        # 실제 프로그램에서 이미지 예시를 matplotlib를 이용해 보여주는 코드
        img = load_img(self.files_root[0])  # 파일들중 첫번쨰 사진 불러오기
        img = img.resize((500, 500))  # 이미지 크기 500X500으로 맞추기
        x = img_to_array(img)  # numpy 배열로 변형
        x = x.reshape((1,) + x.shape)

        idx = 0
        axes = []
        for batch in datagen.flow(x, batch_size=1):
            axes.append(self.fig.add_subplot(3, 3, idx + 1))
            axes[idx].imshow(array_to_img(batch[0]))
            idx += 1
            if idx == 9:
                break

        self.canvas.draw()  # 이미지를 실제로 프로그램에 그려주는 코드

    def generateAndSave(self):
        # 저장할 폴더 위치 가져오기
        save_folder = QFileDialog.getExistingDirectory(self, '저장할 폴더 선택')

        if bool(save_folder):
            # 제너레이터에 넣을 속성값 프로그램에서 가져오기
            count = self.count_spinBox.value()
            horizontalFlip = self.horizontalFlip_comboBox.currentText() == 'True'
            widthShiftRange = self.widthShiftRange_SpinBox.value()
            heightShiftRange = self.heightShiftRange_spinBox.value()
            rotationRange = self.rotationRange_spinBox.value()
            shearRange = self.shearRange_spinBox.value()
            zoomRange = self.zoomRange_spinBox.value()
            verticalFlip = self.verticalFlip_comboBox.currentText() == 'True'
            fillMode = self.fillMode_comboBox.currentText()

            # 사용자 속성에 맞춘 이미지 제너레이터 준비
            datagen = ImageDataGenerator(horizontal_flip=horizontalFlip, width_shift_range=widthShiftRange,
                                         height_shift_range=heightShiftRange, rotation_range=rotationRange,
                                         shear_range=shearRange, zoom_range=zoomRange,
                                         vertical_flip=verticalFlip, fill_mode=fillMode)

            # 프로그레스 창 띄우기
            generating = Generating(len(self.files_root) * count, count, save_folder, datagen, self.files_root)
            generating.exec_()

    def openOptionHelp(self):
        # 옵션 도움말 창 열기
        optionhelp = OptionHelp()
        optionhelp.exec_()

    def openHowToHelp(self):
        # 설명 도움말 창 열기
        howtohelp = HowToHelp()
        howtohelp.exec_()


class Generating(QDialog, generating_class):
    def __init__(self, total_count, count, save_folder, datagen, files_root):
        super().__init__()
        self.setupUi(self)

        # 클래스 내에서 사용할 변수
        self.total_count = total_count  # 전체 이미지 개수
        self.now_count = 0  # 현재 처리된 이미지 개수
        self.count = count
        self.save_folder = save_folder
        self.datagen = datagen
        self.files_root = files_root

        # 이벤트 추가
        self.ok_button.clicked.connect(self.close)  # 버튼을 누르면 해당 창 종료
        QTimer.singleShot(7, self.generateAndSave)  # 대기 거는 코드, 없으면 설정한 ui가 뜨지 않음

    def updateProgress(self):
        self.now_count = self.now_count + 1  # 진행된 갯수 +1 시키기
        nowValue = int(self.now_count / self.total_count * 100)  # 현재 진행 퍼센트 계산
        self.progressbar.setValue(nowValue)  # 값 반영시키기
        time.sleep(0.001)  # 대기 거는 코드, 없으면 프로그레스바 수치가 올라가는것이 표시되지 않는다.

    def generateAndSave(self):
        # 실제로 이미지를 제너레이터를 이용하여 생성하는 코드
        for i in self.files_root:
            img = load_img(i)
            x = img_to_array(img)
            x = x.reshape((1,) + x.shape)
            idx = 0
            for batch in self.datagen.flow(x, batch_size=1):
                name = os.path.splitext(os.path.basename(i))[0]  # 경로에서 이름만 추출해서 name 변수에 저장
                path = self.save_folder + '/' + name + str(idx) + '.jpg'  # 원하는 경로+이미지원본이름+사진 번호+확장자 로 path 지정
                array_to_img(batch[0]).save(path, 'jpeg')  # 실질적으로 이미지 저장하는 코드
                idx += 1
                QTimer.singleShot(1, self.updateProgress)  # 대기 걸면서 프로그레스바 업데이트 함수 실행
                if idx == self.count:
                    break

        self.ok_button.setEnabled(True)  # 확인 버튼 활성화


class HowToHelp(QDialog, howtohelp_class):
    def __init__(self):
        super().__init__()
        self.qPixmap = None
        self.setupUi(self)
        self.explian = ['1. 파일이나 폴더를 연다', '2. 원하는 옵션을 설정한다.',
                        '3. 미리보기 버튼으로 미리 확인한다.(생략 가능)', '4. generate/save 버튼 누른 후 폴더 선택을 한다.',
                        '5. 만드는것을 기다린다.', '6. 해당경로에 이미지가 만들어져 있다.']
        self.images = ['howto_image/howto1.png', 'howto_image/howto2.png', 'howto_image/howto3.png',
                       'howto_image/howto4.png', 'howto_image/howto5.png', 'howto_image/howto6.png']
        self.idx = 0

        # 초기 화면 설정
        self.explain_label.setText(self.explian[self.idx])  # 설명라벨 다시 설정
        # 이미지 라벨 다시 설정
        self.qPixmap = QPixmap()
        self.qPixmap.load(self.images[self.idx])
        self.qPixmap = self.qPixmap.scaled(379, 202)  # 라벨 크기로 조정
        self.image_label.setPixmap(self.qPixmap)

        # 이벤트 추가하기
        self.before_button.clicked.connect(self.before)
        self.next_button.clicked.connect(self.next)

    def before(self):
        # 만약 마지막 페이지였는데 뒤로가기 버튼 누른경우
        if self.idx == 5:
            self.next_button.setEnabled(True)  # 다음으로 가는 버튼 활성화

        self.idx = self.idx - 1  # 이전으로 가야하기 때문에 인덱스번호 1빼기
        self.explain_label.setText(self.explian[self.idx])  # 설명라벨 다시 설정
        # 이미지 라벨 다시 설정
        self.qPixmap = QPixmap()
        self.qPixmap.load(self.images[self.idx])
        self.qPixmap = self.qPixmap.scaled(379, 202)  # 라벨 크기로 조정
        self.image_label.setPixmap(self.qPixmap)

        # 만약 인덱스가 0이 되어버렸다면
        if self.idx == 0:
            self.before_button.setDisabled(True)  # 뒤로가는 버튼 비활성화

    def next(self):
        # 만약 처음 페이지였는데 앞으로가기 버튼 누른경우
        if self.idx == 0:
            self.before_button.setEnabled(True)  # 다음으로 가는 버튼 활성화

        self.idx = self.idx + 1  # 앞으로 가야하기 때문에 인덱스번호 1더하기
        self.explain_label.setText(self.explian[self.idx])  # 설명라벨 다시 설정
        # 이미지 라벨 다시 설정
        self.qPixmap = QPixmap()
        self.qPixmap.load(self.images[self.idx])
        self.qPixmap = self.qPixmap.scaled(379, 202)  # 라벨 크기로 조정
        self.image_label.setPixmap(self.qPixmap)

        # 만약 인덱스가 5가 되어버렸다면
        if self.idx == 5:
            self.next_button.setDisabled(True)  # 앞으로가는 버튼 비활성화


class OptionHelp(QDialog, optionhelp_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # 옵션 리스트
        self.option_list = ['horizontal_flip', 'width_shift_range', 'height_shift_range', 'rotation_range',
                            'shear_range', 'zoom_range', 'vertical_flip',
                            'fill_mode : constant', 'fill_mode : nearest', 'fill_mode : reflect', 'fill_mode : wrap']

        # 이미지 경로 리스트
        self.image_list = ['option_image/horizontal_flip.jpg', 'option_image/width_shift_range.jpg',
                           'option_image/height_shift_range.jpg', 'option_image/rotation_range.jpg',
                           'option_image/shear_range.jpg', 'option_image/zoom_range.jpg',
                           'option_image/vertical_flip.jpg',
                           'option_image/constant.jpg', 'option_image/nearest.jpg', 'option_image/reflect.jpg',
                           'option_image/wrap.jpg']

        # 설명 리스트
        self.example_list = ['수평으로 뒤집는다.', '수직으로 이동시킨다.', '수평으로 이동시킨다.', '이미지를 회전시킨다.',
                             '이미지를 기울린다.', '이미지를 확대 혹은 축소 시킨다.', '수직으로 뒤집는다.',
                             '빈 공간을 그대로 둔다.', '빈 공간을 주변 색으로 채운다.', '빈 공간을 원본 이미지를 대칭시켜 채운다.', '빈 공간을 원본으로 채운다.']

        # 화면 초기 설정
        self.title_label.setText(self.option_list[0])  # 제목 라벨 설정

        # 원본 이미지 넣기
        self.qPixmap1 = QPixmap()
        self.qPixmap1.load('option_image/original.jpg')
        self.qPixmap1 = self.qPixmap1.scaled(138, 152)  # 라벨 크기로 조정
        self.originalImage_label.setPixmap(self.qPixmap1)

        # 속성에 따라 변형된 이미지 넣기
        self.qPixmap2 = QPixmap()
        self.qPixmap2.load(self.image_list[0])
        self.qPixmap2 = self.qPixmap2.scaled(138, 152)  # 라벨 크기로 조정
        self.changeImage_label.setPixmap(self.qPixmap2)

        self.example_label.setText(self.example_list[0])  # 설명 라벨 설정

        # 이벤트 추가
        self.listWidget.itemClicked.connect(self.showExample)
        self.listWidget.itemDoubleClicked.connect(self.showExample)

    def showExample(self):
        # 선택한 아이템의 텍스트를 이용하여 인덱스 찾기
        idx = self.option_list.index(self.listWidget.currentItem().text())

        self.title_label.setText(self.option_list[idx])  # 제목 라벨 설정

        # 속성에 따라 변형된 이미지 넣기
        self.qPixmap = QPixmap()
        self.qPixmap.load(self.image_list[idx])
        self.qPixmap = self.qPixmap.scaled(138, 152)  # 라벨 크기로 조정
        self.changeImage_label.setPixmap(self.qPixmap)

        self.example_label.setText(self.example_list[idx])  # 설명 라벨 설정


# 메인 클래스
if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()
