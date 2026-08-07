Sunday, 2 august , 2026

gpt nói emlearn hiện không hỗ trợ chuyển trực tiếp mô hình QuadraticDiscriminantAnalysis sang C/C++.
đang xem danhh sách các model có thể chuyển đổi được.

Monday, august 3, 2026

    danh sách các model có thể chuyển đổi:
    https://emlearn.readthedocs.io/en/latest/source/README.html?utm_source=chatgpt.com

    đã tạo classifier mới từ model decision tree ( nhẹ hơn random)
    https://colab.research.google.com/drive/1bk95wKzYq3M3umNC5rwlbOJEHAtCVMHN?authuser=1#scrollTo=yO56fAHgmIPl

    classifier mới được lưu trong thư mục AIoT-Server\docs\ai\edge-ser\reports\decision_tree_classifier

Tuesday, august 4, 2026
    tài liệu gpt gợi ý để overfit model 
    https://pandas.pydata.org/pandas-docs/version/2.2/reference/api/pandas.core.groupby.DataFrameGroupBy.sample.html?utm_source=chatgpt.com

    colab để làm overfit
    https://colab.research.google.com/drive/1eVIBfyBqbcsDKhs0MHp5fz_Se6Z3kVSL?usp=sharing

Th aug 6, 2026
    folder overfit:
        https://drive.google.com/drive/folders/1mPT05yS4mRbgqQbV1bMJx62qgojE3i8i?usp=drive_link

    chưa tìm được tài liệu nói về việc cố tình overfit thì nên để mấy sample / nhãn.
    The DecisionTreeClassifier provides parameters such as min_samples_leaf and max_depth to prevent a tree from overfitting. 
        https://scikit-learn.org/stable/auto_examples/tree/plot_cost_complexity_pruning.html?utm_source=chatgpt.com

    sửa phần đọc dữ liệu thành 1 mẫu cho mỗi nhãn Trong train_one_sample.py.

fri aug 7, 2026
    sửa phần đọc dữ liệu thành 1 mẫu cho mỗi nhãn
    Tìm đoạn đang chia train/test.

    Mỗi emotion chỉ giữ 1 sample → Decision Tree học đúng các sample đó → predict lại chính các sample đó → kiểm tra model Python và sau đó model .h có cho cùng kết quả hay không.

    bỏ StratifiedKFold

    https://colab.research.google.com/drive/1eVIBfyBqbcsDKhs0MHp5fz_Se6Z3kVSL?authuser=1#scrollTo=qZ_KRgZ5HvV7

    trong file train_one_sample.py