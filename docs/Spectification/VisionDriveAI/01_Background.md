# 01. Background

## 1.1. Product Overview

VisionDriveAI là một hệ thống AIoT hỗ trợ phát hiện mất tập trung cho người lái xe máy trong môi trường nội đô. Sản phẩm được định hướng như một thiết bị edge nhỏ gọn gắn trên xe, kết hợp camera, cảm biến chuyển động và hệ thống cảnh báo tức thời để giúp người lái nhận biết sớm các hành vi nguy hiểm như ngủ gật, nhìn lạc hướng, cầm điện thoại hoặc điều khiển xe thiếu ổn định.

Trong bối cảnh giao thông đô thị Việt Nam, xe máy là phương tiện di chuyển phổ biến. Tuy nhiên, các tình huống mất tập trung khi lái xe, đặc biệt ở tốc độ thấp trong nội đô, vẫn có thể dẫn đến va chạm, xử lý chậm hoặc tạo nguy hiểm cho người đi đường. Các hành vi như nhìn sang hướng khác quá lâu, mệt mỏi, nhắm mắt, dùng điện thoại hoặc đánh lái bất thường thường xảy ra trong thời gian ngắn nhưng cần được phát hiện và cảnh báo kịp thời.

VisionDriveAI giải quyết vấn đề này bằng cách xử lý dữ liệu trực tiếp trên edge device thay vì phụ thuộc hoàn toàn vào cloud. Camera ghi nhận khuôn mặt và tư thế tay của người lái, cảm biến IMU theo dõi chuyển động tay lái, trong khi hệ thống cảnh báo đa tầng phản hồi bằng rung, âm thanh và đèn LED. Ứng dụng di động hỗ trợ ghi log hành trình, gửi thông báo và phân tích thói quen lái xe dài hạn.

**Slogan sản phẩm:**

> **VisionDriveAI - Tập trung hơn, lái xe an toàn hơn.**

---

## 1.2. Motivation

Động lực phát triển VisionDriveAI xuất phát từ nhu cầu tăng cường an toàn cho người lái xe máy trong môi trường đô thị. Nhiều giải pháp hỗ trợ lái xe an toàn hiện nay tập trung vào ô tô, trong khi xe máy vẫn thiếu các thiết bị nhỏ gọn, chi phí hợp lý và phù hợp với điều kiện sử dụng hằng ngày.

Điện thoại thông minh có thể hỗ trợ định vị hoặc ghi hành trình, nhưng chính điện thoại cũng là một nguyên nhân gây mất tập trung. Người lái xe có thể nhìn màn hình, nghe thông báo hoặc cầm điện thoại khi đang di chuyển. Vì vậy, một thiết bị chuyên biệt có khả năng phát hiện hành vi nguy hiểm và cảnh báo trực tiếp là cần thiết.

VisionDriveAI cũng tận dụng xu hướng Edge AI và AIoT: dữ liệu được xử lý ngay trên thiết bị để giảm độ trễ, hạn chế phụ thuộc Internet liên tục và bảo vệ quyền riêng tư tốt hơn. Việc kết hợp Computer Vision với dữ liệu IMU giúp hệ thống có khả năng phát hiện đa chiều, không chỉ dựa vào hình ảnh hoặc chuyển động riêng lẻ.

---

## 1.3. Intended Audience

VisionDriveAI hướng đến các nhóm người dùng sau:

* Người lái xe máy thường xuyên di chuyển trong nội đô.
* Sinh viên và nhân viên văn phòng đi lại bằng xe máy hằng ngày.
* Tài xế giao hàng, tài xế công nghệ hoặc người chạy xe nhiều giờ liên tục.
* Gia đình muốn theo dõi và nhắc nhở thói quen lái xe an toàn của người thân.
* Đội xe nhỏ hoặc đơn vị vận hành muốn có dữ liệu an toàn theo hành trình.
* Nhóm nghiên cứu hoặc sinh viên muốn triển khai prototype AIoT về Computer Vision và Sensor Fusion.

---

## 1.4. Similar Products and Comparison

### Smartphone Safety Applications

Một số ứng dụng điện thoại có thể theo dõi hành trình, tốc độ hoặc phát hiện phanh gấp. Tuy nhiên, điện thoại không phải lúc nào cũng được đặt ở vị trí quan sát người lái, và việc tương tác với điện thoại khi lái xe có thể tạo thêm rủi ro mất tập trung.

---

### Dashcam and Helmet Camera

Camera hành trình hoặc camera gắn mũ bảo hiểm có thể ghi lại tình huống giao thông, nhưng phần lớn chỉ phục vụ lưu trữ video sau sự kiện. Các thiết bị này thường không tập trung vào phân tích khuôn mặt người lái, hành vi cầm điện thoại hoặc cảnh báo tức thời theo mức độ nguy hiểm.

---

### Automotive Driver Monitoring Systems

Các hệ thống giám sát người lái trên ô tô có thể phát hiện ngủ gật hoặc mất tập trung, nhưng chi phí cao và thiết kế không phù hợp trực tiếp với xe máy. Người dùng xe máy cần một giải pháp nhỏ gọn, dễ lắp đặt và chịu được điều kiện di chuyển linh hoạt hơn.

---

### VisionDriveAI Advantages

So với các giải pháp hiện có, VisionDriveAI có các lợi thế sau:

* Tập trung vào người lái xe máy nội đô, không phải ô tô.
* Xử lý trực tiếp trên edge device, giảm phụ thuộc Internet liên tục.
* Kết hợp camera và IMU để tăng độ tin cậy khi phát hiện hành vi nguy hiểm.
* Cảnh báo đa tầng bằng rung, còi và LED để phản hồi tức thời.
* Có app mobile để ghi log, gửi thông báo và phân tích thói quen lái xe.
* Chi phí prototype tương đối thấp, phù hợp triển khai học thuật và thử nghiệm thực tế.
