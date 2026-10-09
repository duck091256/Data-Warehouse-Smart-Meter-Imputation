# Tên đề tài: Tái cân bằng danh mục thích nghi dựa trên mức độ bất đồng giữa các mô hình PPO
## 1.	Đặt vấn đề: 
PPO là một thuật toán học tăng cường có thể học cách chia tỷ trọng vốn cho nhiều cổ phiếu trong danh mục. Ví dụ, sau khi quan sát dữ liệu thị trường, PPO có thể đề xuất 30% vốn cho FPT, 40% cho VCB và 30% cho HPG. Tuy nhiên, quá trình huấn luyện PPO có yếu tố ngẫu nhiên, nên nếu huấn luyện nhiều lần trên cùng một bộ dữ liệu, mỗi mô hình có thể học ra một cách phân bổ khác nhau. Có mô hình ưu tiên FPT, trong khi mô hình khác lại ưu tiên VCB hoặc HPG. Điều này cho thấy quyết định của PPO có thể chưa ổn định và đặt ra câu hỏi: khi các mô hình PPO không thống nhất với nhau, liệu có nên thay đổi danh mục để tối ưu lợi nhuận?
Khi đó xuất hiện các vấn đề:
-	một mô hình PPO đơn lẻ có thể đưa ra quyết định không ổn định
-	khi các PPO đưa ra quyết định rất khác nhau, việc chọn và tin hoàn toàn vào một PPO có thể gây rủi ro
-	thay đổi danh mục quá nhiều làm tăng chi phí thời gian (t+2 cho chờ mua và t+2 cho chờ bán)
Vấn đề cốt lõi: Có thể sử dụng mức độ bất đồng giữa nhiều PPO để nhận biết khi nào quyết định chưa ổn định và từ đó điều chỉnh mức độ tái cân bằng danh mục hay không?
	Nghiên cứu một phương pháp sử dụng mức độ bất đồng giữa nhiều PPO để kiểm soát việc tái cân bằng danh mục: khi các PPO đồng thuận thì cho phép thay đổi danh mục bình thường; khi các PPO bất đồng mạnh thì hạn chế thay đổi danh mục nhằm giảm tác động của các quyết định không ổn định và chi phí giao dịch
## 2.	Data: 
Dữ liệu thị trường chứng khoán Việt Nam:
-	Các mã VN30 ở thời điểm hiện tại
-	VN-Index để biểu diễn tình trạng chung của thị trường
-	Dữ liệu theo ngày: Open, High, Low, Close, Volume
-	Giai đoạn dự kiến: khoảng 2016–2025

## 3.	Khoảng trống nghiên cứu

| Công trình | Đã giải quyết | Phần còn thiếu so với đề tài |	Link |
| :--- | :--- | :--- | :--- |
| Deep Reinforcement Learning for Automated Stock Trading: An Ensemble Strategy	| Sử dụng PPO, A2C và DDPG. Mỗi giai đoạn chọn agent có kết quả Sharpe tốt nhất để giao dịch. |	Không huấn luyện nhiều PPO cùng loại để đo mức độ khác nhau giữa các quyết định; không sử dụng sự bất đồng đó để điều chỉnh mức rebalance. | https://dl.acm.org/doi/epdf/10.1145/3383455.3422540 |
| Uncertainty-Aware Reinforcement Learning for Portfolio Optimization |	Xây dựng DDPG có xét uncertainty và risk constraint để tránh các quyết định vượt mức rủi ro cho phép. |	Uncertainty không được đo bằng sự bất đồng giữa nhiều PPO về portfolio weights, không nghiên cứu disagreement để điều chỉnh mức rebalance. | https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10749817 |
| FinRL Contests: Data-Driven Financial Reinforcement Learning Agents for Stock and Crypto Trading | Dùng ensemble PPO, SAC, DDPG nhằm giảm policy instability; kết quả của các agent được kết hợp bằng trọng số dựa trên validation Sharpe. | Có ensemble để tăng ổn định nhưng không dùng mức độ các agent bất đồng như một tín hiệu để quyết định rebalance mạnh hay nhẹ. | https://ietresearch.onlinelibrary.wiley.com/doi/epdf/10.1049/aie2.12004 |
| Smart Tangency Portfolio – Yu & Chang, 2025 | PPO/A2C học mức chấp nhận rủi ro và khoảng thời gian rebalance; portfolio weights được tính bởi bộ tối ưu truyền thống.	| Đã điều chỉnh thời điểm rebalance nhưng không dựa vào sự bất đồng giữa nhiều PPO. | https://www.mdpi.com/2227-7072/13/4/227 |


## 4.	Tóm tắt nội dung và các kỹ thuật của nghiên cứu
Quy trình dự kiến:
Market Data → Nhiều PPO → Đo mức bất đồng → Điều chỉnh Rebalancing → Portfolio
Các bước chính:
1.	Thu thập và xử lý dữ liệu giá, khối lượng của các cổ phiếu.
2.	Huấn luyện khoảng 5–10 mô hình PPO có cùng cấu trúc nhưng khác giá trị khởi tạo ngẫu nhiên.
3.	Mỗi PPO đưa ra một tỷ trọng danh mục, ví dụ: FPT 30%, VCB 40%, HPG 30%.
4.	Tính mức độ bất đồng dựa trên sự khác nhau giữa các tỷ trọng mà các PPO đề xuất.
5.	Nếu bất đồng thấp → cho phép chuyển sang danh mục mới.
6.	Nếu bất đồng cao → đưa ra 1 số cách tối ưu 
7.	So sánh
-	Equal Weight
-	PPO đơn
-	PPO Ensemble lấy trung bình
-	Phương pháp đề xuất.
8.	Đánh giá bằng:
-	Lợi nhuận;
-	Sharpe Ratio
-	Maximum Drawdown
-	Số lần/mức độ giao dịch
-	Transaction cost.

