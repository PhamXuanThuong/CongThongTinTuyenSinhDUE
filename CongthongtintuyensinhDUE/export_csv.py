# -*- coding: utf-8 -*-
import csv

qa_data = [
    [
        'ID',
        'ChuDe',
        'PhanLoai',
        'CauHoi_User_Variants',
        'CauTraLoi_ChiTiet',
        'TuKhoa_Search',
        'Nguon_ThamKhao'
    ],
    # 1. TỔNG QUAN VỀ TRƯỜNG
    [
        'DUE_01',
        'Tổng quan Nhà trường',
        'GioiThieuChung',
        'Trường Đại học Kinh tế - Đại học Đà Nẵng là trường gì? | Giới thiệu về trường DUE? | Tên tiếng Anh của DUE là gì? | Mã trường DUE là gì? | DUE ở đâu? | Số điện thoại tuyển sinh DUE?',
        'Trường Đại học Kinh tế – Đại học Đà Nẵng (tên tiếng Anh: University of Economics – The University of Danang, viết tắt: DUE, mã tuyển sinh: DDK) là trường đại học công lập đầu ngành khối kinh tế, kinh doanh và quản lý hàng đầu tại miền Trung - Tây Nguyên và cả nước. Trường trực thuộc Đại học Đà Nẵng (Đại học Vùng trọng điểm quốc gia). Địa chỉ trụ sở: Số 71 Ngũ Hành Sơn, phường Mỹ An, quận Ngũ Hành Sơn, TP. Đà Nẵng. Hotline tư vấn tuyển sinh: 0236 3836 169. Website chính thức: https://due.udn.vn.',
        'tổng quan, giới thiệu, mã trường, ddk, due, địa chỉ, số điện thoại, hotline, tên tiếng anh, đại học kinh tế đà nẵng',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_02',
        'Lịch sử 50 năm DUE',
        'LichSuPhatTrien',
        'Trường DUE thành lập năm nào? | DUE có bao nhiêu năm truyền thống? | Lịch sử hình thành trường Đại học Kinh tế Đà Nẵng? | Chuyến tàu ký ức 50 năm DUE là gì? | Bao nhiêu sinh viên đã tốt nghiệp DUE?',
        'Trường Đại học Kinh tế – Đại học Đà Nẵng có tiền thân là Khoa Kinh tế được thành lập vào tháng 10 năm 1975 ngay sau ngày đất nước thống nhất. Năm 2025 đánh dấu cột mốc tròn 50 năm xây dựng và phát triển (1975 - 2025) với thông điệp: "Chuyến tàu ký ức 50 DUE - Nửa thế kỷ kiến tạo và phụng sự". Trải qua 50 năm, trường đã đào tạo hơn 70.000 cử nhân, thạc sĩ, tiến sĩ cung ứng nguồn nhân lực chất lượng cao cho đất nước.',
        'thành lập năm nào, 1975, 50 năm, chuyến tàu ký ức, truyền thống, 70000 cử nhân, bề dày lịch sử',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    # 2. BỐN GIAI ĐOẠN LỊCH SỬ
    [
        'DUE_03',
        'Giai đoạn 1 (1975 - 1985)',
        'LichSuPhatTrien',
        'Giai đoạn đầu thành lập trường như thế nào? | Khoa Kinh tế thành lập khi nào? | Khóa đầu tiên DUE đào tạo những ngành gì? | 6 ngành đầu tiên của DUE?',
        'Giai đoạn từ tháng 10/1975 đến tháng 12/1985: Tháng 10 năm 1975, Khoa Kinh tế thuộc Viện Đại học Đà Nẵng (sau đó là Đại học Bách khoa Đà Nẵng) chính thức được thành lập và tuyển sinh khóa đại học chính quy đầu tiên. Mục tiêu là đào tạo cán bộ kinh tế phục vụ công cuộc tái thiết sau chiến tranh. Giai đoạn này Khoa đào tạo 6 chuyên ngành chủ lực: 1. Kế hoạch hóa Kinh tế Quốc dân; 2. Kinh tế Công nghiệp; 3. Kinh tế Nông nghiệp; 4. Kinh tế Thương nghiệp; 5. Thống kê; 6. Kế toán.',
        'giai đoạn 1, 1975 1985, thành lập khoa kinh tế, 6 chuyên ngành đầu tiên, kế hoạch hóa, công nghiệp, nông nghiệp, thương nghiệp, thống kê, kế toán',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_04',
        'Giai đoạn 2 (1985 - 1988)',
        'LichSuPhatTrien',
        'Phân hiệu Đại học Kinh tế Đà Nẵng thành lập khi nào? | Phân hiệu Kinh tế Bắc Mỹ An gồm những khoa nào? | Lịch sử DUE giai đoạn 1985 - 1988?',
        'Giai đoạn từ tháng 12/1985 đến tháng 10/1988: Khối ngành Kinh tế được tách ra để thành lập Phân hiệu Đại học Kinh tế Đà Nẵng đặt tại Bắc Mỹ An (nay là số 71 Ngũ Hành Sơn). Phân hiệu thời điểm đó tổ chức gồm 3 khoa đào tạo: 1. Khoa Công Thương; 2. Khoa Thống kê - Kế toán - Tài chính; 3. Khoa Tại chức. Đây là dấu mốc quan trọng khẳng định cơ sở đào tạo độc lập đầu tiên tại địa chỉ hiện nay của Nhà trường.',
        'phân hiệu đại học kinh tế đà nẵng, 1985 1988, bắc mỹ an, 71 ngũ hành sơn, khoa công thương, khoa thống kê kế toán tài chính, khoa tại chức',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_05',
        'Giai đoạn 3 (1988 - 1994)',
        'LichSuPhatTrien',
        'Giai đoạn 1988 đến 1994 của DUE diễn ra như thế nào? | Vì sao DUE tái sáp nhập vào Bách khoa năm 1988?',
        'Giai đoạn từ tháng 10/1988 đến tháng 04/1994: Thực hiện chủ trương sắp xếp, tinh gọn mạng lưới các trường đại học thời kỳ đầu Đổi mới của Nhà nước, Phân hiệu Đại học Kinh tế sáp nhập trở lại thành Khoa Kinh tế thuộc Trường Đại học Bách khoa Đà Nẵng. Trong giai đoạn này, khoa củng cố chất lượng chuyên môn, đổi mới giáo trình và chuẩn bị đầy đủ nhân lực, tiền đề để thành lập một trường đại học kinh tế độc lập quy mô vùng.',
        '1988 1994, sáp nhập bách khoa, đổi mới, tinh gọn, tiền đề đại học đà nẵng',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_06',
        'Giai đoạn 4 (1994 - Nay)',
        'LichSuPhatTrien',
        'Trường Đại học Kinh tế chính thức thành lập năm nào? | Nghị định 32/CP liên quan gì đến DUE? | Quá trình phát triển từ 1994 đến nay của DUE?',
        'Giai đoạn từ tháng 04/1994 đến nay: Ngày 04/04/1994, Chính phủ ban hành Nghị định số 32/CP thành lập Đại học Đà Nẵng. Trên cơ sở đó, Trường Đại học Kinh tế chính thức trở thành trường đại học thành viên độc lập trong hệ thống Đại học Đà Nẵng. Trường phát triển vượt bậc về quy mô đào tạo, đạt chuẩn kiểm định chất lượng quốc tế AUN-QA, đào tạo đa ngành với hơn 30 chuyên ngành kinh tế số, hội nhập quốc tế toàn diện.',
        '1994 đến nay, nghị định 32/cp, 04/04/1994, thành lập trường đại học kinh tế, đại học đà nẵng, aun-qa, hội nhập',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    # 3. SỨ MẠNG, TẦM NHÌN, GIÁ TRỊ CỐT LÕI
    [
        'DUE_07',
        'Sứ mạng của DUE',
        'SuMangTamNhin',
        'Sứ mạng của trường Đại học Kinh tế Đà Nẵng là gì? | Sứ mệnh DUE là gì? | DUE có nhiệm vụ gì?',
        'Sứ mạng chính thức của Trường Đại học Kinh tế – Đại học Đà Nẵng: "Chúng tôi kiến tạo môi trường học thuật tiên tiến và nhân văn; thúc đẩy, khám phá, ứng dụng và chuyển giao tri thức gắn với biến đổi số, đổi mới sáng tạo và phát triển bền vững; nâng cao năng lực học tập suốt đời; nuôi dưỡng và phát triển tài năng phục vụ sự phát triển của cộng đồng."',
        'sứ mạng, sứ mệnh, nhiệm vụ, tri thức, chuyển đổi số, đổi mới sáng tạo, phát triển bền vững, học tập suốt đời',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_08',
        'Tầm nhìn của DUE',
        'SuMangTamNhin',
        'Tầm nhìn của trường Đại học Kinh tế Đà Nẵng là gì? | Mục tiêu phát triển tương lai của DUE? | Viễn cảnh của DUE?',
        'Tầm nhìn (Viễn cảnh) của Trường Đại học Kinh tế – Đại học Đà Nẵng: "Khát vọng của chúng tôi là trở thành trường đại học hàng đầu Việt Nam, đóng góp vào sự thịnh vượng của cộng đồng ASEAN và tri thức nhân loại." Mục tiêu khẳng định vị thế trung tâm đào tạo và nghiên cứu học thuật đẳng cấp khu vực.',
        'tầm nhìn, viễn cảnh, mục tiêu tương lai, hàng đầu việt nam, asean, thịnh vượng cộng đồng, nhân loại',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_09',
        '5 Giá trị cốt lõi của DUE',
        'GiaTriCotLoi',
        '5 giá trị cốt lõi của DUE là gì? | Các giá trị văn hóa của Trường Đại học Kinh tế Đà Nẵng? | Triết lý giá trị DUE?',
        'Trường Đại học Kinh tế – Đại học Đà Nẵng định hướng hành vi và văn hóa tổ chức qua 5 Giá trị cốt lõi: 1. CHÍNH TRỰC: Tôn trọng sự thật, tính minh bạch và chuẩn mực đạo đức; 2. HỢP TÁC: Đề cao tinh thần hợp tác, làm việc nhóm và hỗ trợ lẫn nhau; 3. TÔN TRỌNG: Tôn trọng cá nhân, bảo vệ môi trường thiên nhiên và chấp nhận sự khác biệt; 4. CẢM THÔNG: Thúc đẩy sự sẻ chia, thấu cảm và đồng cảm với cộng đồng; 5. SÁNG TẠO: Khuyến khích tinh thần đổi mới sáng tạo, khởi nghiệp và khám phá không ngừng.',
        'giá trị cốt lõi, 5 giá trị, chính trực, hợp tác, tôn trọng, cảm thông, sáng tạo, văn hóa due',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_10',
        'Kiểm định chất lượng AUN-QA',
        'ChatLuongDaoTao',
        'DUE đạt chuẩn kiểm định chất lượng gì? | Bằng cấp DUE có được quốc tế công nhận không? | Kiểm định AUN-QA tại DUE?',
        'Trường Đại học Kinh tế – Đại học Đà Nẵng đạt chuẩn kiểm định cơ sở giáo dục đại học quốc gia và chuẩn kiểm định mạng lưới các trường đại học Đông Nam Á (AUN-QA). Các chương trình đào tạo mũi nhọn (Quản trị kinh doanh, Kế toán, Tài chính - Ngân hàng, Marketing, Kinh doanh quốc tế,...) đều đạt chuẩn AUN-QA, đảm bảo giá trị bằng cấp và khả năng liên thông, hội nhập nghề nghiệp quốc tế.',
        'kiểm định chất lượng, aun-qa, đông nam á, quốc tế, bằng cấp quốc tế, chất lượng giáo dục',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    # 4. QUY MÔ, CÁC KHOA VÀ CƠ SỞ VẬT CHẤT
    [
        'DUE_11',
        'Quy mô và Ngành đào tạo',
        'NganhHoc',
        'DUE có bao nhiêu ngành học? | Các khoa của trường DUE? | Các ngành đào tạo tại DUE?',
        'DUE hiện đào tạo 31 ngành và chuyên ngành đại học thuộc các khoa: Khoa Quản trị kinh doanh, Khoa Tài chính - Ngân hàng, Khoa Kế toán, Khoa Marketing, Khoa Kinh doanh quốc tế, Khoa Kinh tế, Khoa Thương mại điện tử & Kinh tế số, Khoa Luật, Khoa Thống kê - Tin học, Khoa Du lịch. Cung cấp các hệ: Cử nhân Chính quy, Chất lượng cao, Liên kết quốc tế 2+2, Thạc sĩ và Tiến sĩ.',
        'ngành học, chuyên ngành, các khoa, quản trị kinh doanh, tài chính ngân hàng, kế toán, marketing, kinh tế số, logistics, du lịch, luật',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ],
    [
        'DUE_12',
        'Khuôn viên và Cơ sở vật chất',
        'CoSoVatChat',
        'Cơ sở vật chất của DUE như thế nào? | Trường DUE nằm ở đâu? | Thư viện và ký túc xá DUE?',
        'DUE tọa lạc tại 71 Ngũ Hành Sơn, Đà Nẵng với không gian xanh, hiện đại: 100% giảng đường thông minh có điều hòa, máy chiếu; Thư viện số hiện đại kết nối dữ liệu quốc tế; Phòng thực hành Fintech Lab, mô phỏng doanh nghiệp, máy tính cấu hình cao; Ký túc xá tiện nghi gần biển Mỹ Khê và khu liên hợp thể thao dành cho sinh viên.',
        'cơ sở vật chất, khuôn viên, thư viện, ký túc xá, giảng đường thông minh, fintech lab, 71 ngũ hành sơn',
        'https://due.udn.vn/vi-vn/gioithieu/gioithieugt/cid/71'
    ]
]

# Xuất 2 file CSV (thư mục gốc và thư mục Django)
paths = [
    'due_chatbot_knowledge.csv',
    'lich_su_va_su_mang_due.csv',
    'CongthongtintuyensinhDUE/due_chatbot_knowledge.csv',
    'CongthongtintuyensinhDUE/lich_su_va_su_mang_due.csv'
]

for p in paths:
    with open(p, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(qa_data)

print('Successfully written CSV files.')
