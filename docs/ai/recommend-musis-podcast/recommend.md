# Gợi ý nhạc và podcast cho EmotiCare

## Mục tiêu

Đề xuất nhạc và podcast ngắn phù hợp với **cảm xúc hiện tại**, **mục đích sử dụng** và **phản hồi nghe trước đây** của mỗi người dùng. Hệ thống phục vụ chăm sóc tinh thần hằng ngày, không thay thế chẩn đoán hoặc tư vấn y tế.

Ví dụ:

- `stressed` + mục tiêu “bình tĩnh trong 5 phút” → nhạc ambient nhẹ hoặc podcast hướng dẫn thở ngắn.
- `tired` + mục tiêu “lấy lại sự tập trung” → nhạc nhịp vừa, ít lời hoặc podcast tập trung ngắn.
- `sad` → nội dung hỗ trợ, ấm áp; không ép người dùng phải nghe nội dung quá tích cực.

## Hiện trạng trong dự án

Server đã có nền tảng cần thiết:

- `MediaItem`: bài hát/podcast, loại nội dung, category, thời lượng và URL phát.
- `MediaSelectionLog`: lịch sử người dùng chọn nội dung, category, ý định và điểm đánh giá.
- Mapping `emotion -> category`: `relax`, `focus`, `sleep`, `happy`, `sad_support`, `anger_release`, `energy_recover`.
- Endpoint riêng cho nhạc và podcast: `/api/media/music/recommend`, `/api/media/podcast/recommend`.

Vì dữ liệu tương tác ban đầu còn ít, **không nên bắt đầu bằng collaborative filtering hoặc mô hình deep learning**. Cách phù hợp nhất là hybrid ranker có thể giải thích, chạy trực tiếp trong service Python hiện tại và dần học từ feedback.

## Thuật toán đề xuất: Contextual Hybrid Ranking

Mỗi request tạo một danh sách ứng viên từ `MediaItem`, sau đó xếp hạng bằng tổng điểm có trọng số:

```text
score(u, i, c) =
  0.40 * emotion_fit(i, c)
+ 0.25 * personal_feedback(u, i)
+ 0.15 * recent_context(u, i)
+ 0.10 * novelty(u, i)
+ 0.10 * diversity(i)
```

Trong đó `u` là người dùng, `i` là media item và `c` là context của phiên (cảm xúc, mục tiêu, thời điểm, thời lượng rảnh).

### 1. Lấy ứng viên

1. Lọc item đang `enabled` và đúng `media_type` (`song` hoặc `podcast`).
2. Lấy category từ cảm xúc và mục tiêu người dùng.
3. Với podcast, lọc thêm theo thời lượng mong muốn, ví dụ `<= 5 phút`, `5-15 phút`, hoặc `> 15 phút`.
4. Loại item bị người dùng `dislike` hoặc đã nghe gần đây, trừ khi họ từng `like` mạnh.

### 2. Tính điểm

| Thành phần | Cách tính đề xuất | Lý do |
| --- | --- | --- |
| `emotion_fit` | 1.0 cho category ưu tiên đầu, 0.6 cho category thứ hai; cộng điểm nếu goal khớp | Cảm xúc là tín hiệu chính của EmotiCare. |
| `personal_feedback` | Chuẩn hóa từ rating, like, completion rate và skip | Người dùng cần được học theo phản hồi cá nhân. |
| `recent_context` | Tăng điểm nếu cùng chủ đề với 3-5 item gần nhất mà người dùng nghe hết/đánh giá tốt | Podcast có xu hướng tiêu thụ theo chuỗi chủ đề ngắn. |
| `novelty` | Phạt item đã được đề xuất/nghe gần đây; thưởng item mới nhưng cùng profile | Tránh lặp lại và vẫn tạo khám phá. |
| `diversity` | Re-rank, không để nhiều item cùng creator/category liên tiếp | Danh sách ngắn vẫn cần đa dạng. |

### 3. Re-rank kết quả

Sau khi lấy top 10 theo score, chọn top 5 theo quy tắc đa dạng:

- Không quá 2 item của cùng creator.
- Không quá 2 item cùng category liên tiếp.
- Ít nhất 1 item có novelty cao nếu người dùng đã có lịch sử.
- Với podcast, ưu tiên episode hơn là chỉ gợi ý show chung chung.

Trả về trường `reason` để UI giải thích, ví dụ: “Phù hợp với trạng thái căng thẳng; bạn từng nghe hết nội dung thư giãn tương tự.”

## Nhạc và podcast cần tín hiệu khác nhau

| Nội dung | Tín hiệu tích cực | Tín hiệu tiêu cực | Mục tiêu ranking |
| --- | --- | --- | --- |
| Nhạc | play lặp lại, like, nghe >70% | skip trước 15-30 giây, dislike | tạo playlist ngắn hợp mood, có khám phá vừa phải |
| Podcast | play, completion rate, follow/save, nghe tiếp episode sau | bỏ dở sớm, dislike | khớp chủ đề, mục tiêu và thời lượng có thể dành ra |

Do đó nên bổ sung event log thay vì chỉ lưu đánh giá 1-5:

```text
impression | open | play | progress | complete | skip | like | dislike
```

Các field tối thiểu: `event_type`, `played_seconds`, `completion_rate`, `occurred_at`, `recommendation_id`, `media_item_id`, `session_id`.

## Lộ trình triển khai

### Pha 1 — MVP có thể demo

1. Sửa `/api/recommendations/request` để trả 1 activity + 2 song + 2 podcast, thay vì chỉ activity.
2. Dùng ranking theo emotion/category hiện tại, feedback score và anti-repeat.
3. Simulator phát `source_url`, có nút thích/không phù hợp và gửi feedback.
4. Hiển thị `reason` cho từng gợi ý.

### Pha 2 — Cá nhân hóa theo hành vi

1. Bổ sung bảng hoặc mở rộng log sự kiện phát media.
2. Tính completion rate và early skip rate.
3. Thêm mục tiêu rõ ràng: thư giãn, tập trung, ngủ, lấy năng lượng, quản lý cảm xúc.
4. Áp dụng điểm `recent_context`, novelty và re-rank đa dạng.

### Pha 3 — Khi đã có đủ dữ liệu

1. Thử item-to-item collaborative filtering hoặc matrix factorization như một candidate generator.
2. Kết hợp điểm CF vào hybrid ranker, không thay thế các rule an toàn theo cảm xúc.
3. Đánh giá offline bằng Precision@5, NDCG@5, coverage, diversity và completion rate.
4. Có thể dùng LLM để tạo profile/đánh giá offline, không dùng LLM làm ranker thời gian thực đầu tiên.

## Tiêu chí đánh giá

- `CTR/open rate`: tỷ lệ mở nội dung sau khi được hiển thị.
- `Play rate`: tỷ lệ bắt đầu phát.
- `Early skip rate`: tỷ lệ bỏ sớm; càng thấp càng tốt.
- `Completion rate`: đặc biệt quan trọng cho podcast.
- `Like/dislike rate` và rating trung bình đã chuẩn hóa theo từng user.
- `NDCG@5`, `Precision@5`: đánh giá offline khi có log đủ lớn.
- `Coverage` và `intra-list diversity`: kiểm soát việc chỉ lặp vài item phổ biến.

## Tài liệu tham khảo

1. Benton, G. et al. (2020), **Trajectory Based Podcast Recommendation**. Bài báo cho thấy podcast nên được xem là hành vi tuần tự; lịch sử gần đây là tín hiệu quan trọng để gợi ý tập tiếp theo.  
   https://arxiv.org/abs/2009.03859

2. Chen, C.-W. et al. (2022), **Enabling Goal-Focused Exploration of Podcasts in Interactive Recommender Systems (GoalPods)**. Nghiên cứu Spotify cho thấy podcast cần xét mục tiêu rõ ràng của người dùng, không chỉ hành vi quá khứ.  
   https://research.atspotify.com/publications/enabling-goal-focused-exploration-of-podcasts-in-interactive-recommender-systems

3. Zamani, H. et al. (2018), **An Analysis of Approaches Taken in the ACM RecSys Challenge 2018 for Automatic Music Playlist Continuation**. Nguồn tham khảo cho ranking theo playlist/chuỗi nhạc và các metric R-precision, NDCG, recommended-song clicks.  
   https://arxiv.org/abs/1810.01520

4. Garcia-Gathright, J. et al. (2018), **Understanding and Evaluating User Satisfaction with Music Discovery**. Spotify chỉ ra cần đánh giá theo mức độ hài lòng và hành vi đã chuẩn hóa theo từng người dùng, không chỉ tổng số lượt nghe.  
   https://research.atspotify.com/2018/7/understanding-and-evaluating-user-satisfaction-with-music-discovery

5. Fabbri, F. et al. (2025), **Evaluating Podcast Recommendations with Profile-Aware LLM-as-a-Judge**. Gợi ý dùng profile ngôn ngữ tự nhiên và LLM ở tầng đánh giá offline khi hệ thống đã có lịch sử nghe đủ dài.  
   https://research.atspotify.com/publications/evaluating-podcast-recommendations-with-profile-aware-llm-as-a-judge

6. Mizuno, J., Ogata, J., & Goto, M. (2008), **A Similar Content Retrieval Method for Podcast Episodes**. Chỉ ra transcript/nội dung nói có thể dùng để tính tương đồng episode, hữu ích cho podcast thiếu metadata tốt.  
   https://doi.org/10.1109/SLT.2008.4777899

## Kết luận

Thuật toán phù hợp nhất ở giai đoạn hiện tại là **Contextual Hybrid Ranking**: rule theo cảm xúc và mục tiêu làm nền, feedback cá nhân + lịch sử gần đây để cá nhân hóa, novelty/diversity để tránh lặp. Nó khả thi với schema hiện có, giải thích được cho người dùng và tạo dữ liệu tốt để nâng cấp sang collaborative filtering về sau.
