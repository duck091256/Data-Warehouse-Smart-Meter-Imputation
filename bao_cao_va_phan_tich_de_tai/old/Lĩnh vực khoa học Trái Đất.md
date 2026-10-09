# Kết quả khảo sát bước 2–4

Tôi không tìm thấy tài liệu nền nào trong workspace hiện tại, nên kết quả dưới đây dựa trên các nguồn công khai và paper/hệ thống gốc đã kiểm tra đến ngày 29/08/2026.

Kết luận sớm: hướng có triển vọng nhất là **kho dữ liệu sự kiện ngập có kiểm soát chất lượng và căn chỉnh thời gian**, giới hạn trong **một vùng ngập cụ thể ở Đồng bằng sông Cửu Long**. Hướng này phù hợp môn Kho dữ liệu hơn việc xây một “nền tảng quan sát Trái đất” rộng.

## 1. Khảo sát các hệ thống/paper gần nhất

| Nguồn                                  | Dữ liệu                                                               | Cách tổ chức/xử lý                                                                                               | Phần còn bỏ sót hoặc chưa xử lý tốt                                                                                                                                                                                                                                                                                                                                                           |
| -------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **GeoCube**                            | Dữ liệu raster và vector địa không gian đa nguồn                      | Data cube với các chiều không gian, thời gian, nguồn dữ liệu; hỗ trợ truy vấn và xử lý địa không gian quy mô lớn | Tập trung vào hạ tầng cube tổng quát, chưa giải quyết sâu chất lượng quan sát, thiếu dữ liệu và sai lệch thời gian theo từng sự kiện cụ thể. [GeoCube](https://doi.org/10.1080/13658816.2022.2087222)                                                                                                                                                                                         |
| **ecodatacube.eu**                     | Sentinel-1, Sentinel-2, DEM, land cover, climate data                 | Cube môi trường phân tích sẵn cho châu Âu; có lớp chất lượng và gap-filling                                      | Chính paper thừa nhận gap-filling có thể che khuất thay đổi thực tế; temporal aggregation có thể làm mất biến động ngắn hạn. [ecodatacube.eu](https://pmc.ncbi.nlm.nih.gov/articles/PMC10252825/)                                                                                                                                                                                             |
| **Ocean-DC**                           | Landsat-8/9, Sentinel-2 cho vùng cảng và sự kiện tràn dầu             | Hợp nhất ảnh thành NetCDF 4D trước–trong–sau sự kiện                                                             | Chủ yếu chứng minh khả năng tạo cube ảnh; chưa đưa ra cơ chế tổng quát để đánh giá độ đầy đủ, độ trễ và mức tin cậy giữa các nguồn. [Ocean-DC](https://arxiv.org/abs/2405.06730)                                                                                                                                                                                                              |
| **NASA Harmony / Earthdata GIS**       | Nhiều bộ dữ liệu Earth observation từ NASA                            | Chuẩn hóa truy cập, chuyển đổi projection/format, subset theo không gian; cung cấp dịch vụ OGC/API               | Giải quyết truy cập và chuyển đổi dữ liệu ở cấp nền tảng, không phải một warehouse sự kiện với fact, dimension, quality history và các phép đo nghiệp vụ cụ thể. [Harmony](https://harmony.earthdata.nasa.gov/), [Earthdata GIS](https://gis.earthdata.nasa.gov/)                                                                                                                             |
| **Copernicus Data Space STAC**         | Sentinel-1, Sentinel-2, Sentinel-3 và các bộ dữ liệu bổ trợ           | Catalog metadata theo không gian–thời gian; hỗ trợ tìm kiếm bằng STAC/CQL2                                       | STAC giúp tìm và lấy asset, nhưng không tự giải quyết việc nhiều ảnh khác ngày, khác độ phân giải, thiếu quan sát hoặc dữ liệu bị gap-filling. Copernicus cũng mô tả STAC là lớp bổ sung cho catalog OData, không phải warehouse phân tích hoàn chỉnh. [STAC documentation](https://documentation.dataspace.copernicus.eu/APIs/STAC.html)                                                     |
| **USGS ComCat + ShakeMap**             | Earthquake catalog, ground motion, intensity, station measurements    | Catalog sự kiện; ShakeMap tạo các trường cường độ rung và sản phẩm không gian                                    | ComCat và ShakeMap rất hữu ích nhưng vẫn là các sản phẩm theo catalog/event. Việc hợp nhất phiên bản cập nhật, chất lượng quan sát, địa hình và truy vấn so sánh nhiều sự kiện không phải mục tiêu chính. [ComCat](https://www.usgs.gov/programs/earthquake-hazards/anss-comprehensive-earthquake-catalog-comcat-documentation), [ShakeMap](https://earthquake.usgs.gov/data/shakemap/atlas/) |
| **NOAA Climate Data Online**           | Quan trắc khí tượng, station, climate measurements                    | API tổ chức theo dataset, station, location, data type                                                           | Có API và metadata nhưng cần token, giới hạn request; không cung cấp sẵn mô hình liên kết event–satellite–rainfall phù hợp với một bài toán thiên tai hẹp. [NOAA CDO API](https://www.ncei.noaa.gov/cdo-web/webservices/getstarted)                                                                                                                                                           |
| **Sentinel-1 Global Flood Monitoring** | Sentinel-1 GRD, surface water, forest, settlement và ancillary layers | Global Sentinel-1 data cube; kết hợp nhiều bộ phân loại flood và tạo flood likelihood                            | Đây là hệ thống rất gần với hướng ngập. Tuy nhiên, nó phục vụ monitoring toàn cầu/near-real-time; còn bài toán hẹp về audit chất lượng, căn chỉnh với rainfall và truy vấn theo từng sự kiện/lưu vực vẫn còn chỗ để nghiên cứu ở quy mô sinh viên. [GFM paper](https://doi.org/10.1016/j.rse.2025.115108)                                                                                     |

Điểm quan trọng: không nên tuyên bố “chưa ai làm data cube ngập”. Điều đó sai vì đã có GFM, STAR và nhiều hệ thống Sentinel-1 cube. Khe hở hợp lý hơn là:

> Các hệ thống hiện có tối ưu cho catalog, phân phối ảnh hoặc monitoring diện rộng; chưa tập trung vào một warehouse nhỏ, event-centric, có thể đo được ảnh hưởng của missingness, temporal misalignment và chất lượng nguồn dữ liệu khi trả lời truy vấn thiên tai.

## 2. Bản đồ nghiên cứu

| Hiện tượng / vấn đề kỹ thuật | Tích hợp đa nguồn | Chuẩn hóa / ARD | Cập nhật liên tục |               Chất lượng và thiếu dữ liệu | Mô hình không gian–thời gian |
| ---------------------------- | ----------------: | --------------: | ----------------: | ----------------------------------------: | ---------------------------: |
| Khí hậu                      |               Cao |             Cao |        Trung bình |                                       Cao |                          Cao |
| Thiên tai ngập               |               Cao |             Cao |               Cao | **Trung bình–thưa ở cấp event warehouse** |                          Cao |
| Động đất                     |        Trung bình |      Trung bình |               Cao |                                Trung bình |                          Cao |
| Hải dương / ven biển         |               Cao |             Cao |        Trung bình |                                Trung bình |                          Cao |
| Cháy rừng                    |               Cao |             Cao |               Cao |                                Trung bình |                          Cao |
| Địa chất                     |        Trung bình |      Trung bình |              Thấp |                                Trung bình |                   Trung bình |

Các ô đã được nghiên cứu nhiều nhất là:

- data cube ảnh viễn thám;
- STAC/catalog và truy cập cloud;
- monitoring gần thời gian thực;
- chuẩn hóa ảnh Sentinel;
- truy vấn không gian–thời gian.

Các ô còn thưa hơn và phù hợp bài toán sinh viên:

- quality-aware warehouse cho một loại thiên tai hẹp;
- lưu vết phiên bản và nguồn gốc dữ liệu theo từng sự kiện;
- đo ảnh hưởng của dữ liệu thiếu và lệch thời gian lên kết quả tổng hợp;
- liên kết raster observation với rainfall/gauge/DEM trong schema dạng dimensional warehouse.

## 3. Ba khoảng trống cụ thể

### Khoảng trống A — Ngập lụt

Các hệ thống như GFM đã có cube Sentinel-1 toàn cầu và nhiều lớp ancillary. Tuy nhiên, chúng không được thiết kế chủ yếu để trả lời câu hỏi dạng:

> Trong một sự kiện ngập cụ thể, kết quả diện tích ngập thay đổi thế nào nếu loại bỏ ảnh thiếu, ảnh có quality flag thấp hoặc rainfall không cùng cửa sổ thời gian?

Nguồn dữ liệu công khai:

- Copernicus Sentinel-1 GRD qua CDSE STAC;
- NASA GPM IMERG rainfall;
- NASA/USGS SRTM DEM;
- có thể dùng thêm Global Surface Water làm lớp tham chiếu.

### Khoảng trống B — Động đất

USGS cung cấp ComCat, ShakeMap Atlas và các sản phẩm ground-motion khá đầy đủ. Một paper gần đây cũng đã xây spatio-temporal earthquake data warehouse cho dữ liệu châu Âu. Vì vậy, không thể lấy “xây kho dữ liệu động đất” làm tính mới.

Khe hẹp còn lại là:

> warehouse có version/provenance cho việc theo dõi một event từ catalog ban đầu đến ShakeMap được cập nhật, đồng thời đo tác động của việc thay đổi sản phẩm lên truy vấn vùng chịu rung mạnh.

Nguồn dữ liệu:

- USGS ComCat API;
- USGS ShakeMap Atlas/API;
- SRTM DEM hoặc USGS elevation;
- có thể giới hạn ở Philippines hoặc một vùng Đông Nam Á.

Rủi ro: paper năm 2026 về earthquake warehouse làm giảm tính mới của hướng này.

### Khoảng trống C — Cháy rừng

NASA FIRMS cung cấp hotspot từ MODIS/VIIRS; ERA5 hoặc dữ liệu khí tượng có thể cung cấp gió, nhiệt độ và độ ẩm. Nhưng nhiều hệ thống chỉ cung cấp điểm hotspot hoặc bản đồ hiển thị, chưa tập trung vào việc đánh giá:

> dữ liệu hotspot bị thiếu do mây/quỹ đạo vệ tinh ảnh hưởng thế nào đến thống kê số vụ cháy theo ngày, huyện và loại thảm phủ?

Nguồn dữ liệu:

- NASA FIRMS;
- Copernicus/ERA5;
- SRTM DEM;
- ESA WorldCover hoặc MODIS land cover.

Rủi ro: “fire monitoring” đã có nhiều nghiên cứu; tính mới chỉ đủ nếu khóa vào quality-aware aggregation và một khu vực cụ thể.

## 4. Ba đề tài ứng viên

| Ứng viên                                                                                | Vấn đề Y                                                                                                                                                                           | Khác gì hệ thống hiện có                                                                                                                                                  | Dữ liệu                                                                                               | Cách đo W                                                                                                                                                                      | Rủi ro và khối lượng                                                                                                                                                        |
| --------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A. Kho dữ liệu chất lượng-aware cho truy vấn sự kiện ngập ở Đồng bằng sông Cửu Long** | Ảnh Sentinel-1, rainfall và DEM khác thời gian, độ phân giải và mức đầy đủ. Các hệ thống hiện có chưa cho thấy rõ dữ liệu thiếu/lệch thời gian làm thay đổi chỉ số sự kiện ra sao. | GFM tối ưu monitoring toàn cầu; Ocean-DC tối ưu tạo cube ảnh. Đề tài này tập trung vào warehouse event-centric, quality dimension và audit kết quả truy vấn.              | Sentinel-1 GRD, GPM IMERG, SRTM DEM, Global Surface Water. Các nguồn đều công khai; CDSE có STAC API. | So sánh: diện tích ngập theo event, rainfall trước–trong–sau event, coverage ratio, số pixel thiếu, độ trễ ingestion, kết quả khi thay đổi ngưỡng quality và cửa sổ thời gian. | Rủi ro xử lý raster nặng. Giảm bằng cách chọn 5–10 sự kiện, 1–2 tỉnh hoặc một tiểu vùng, chỉ lưu statistics/tiles đã cắt. Khối lượng: **khả thi cao với 2 người/1 học kỳ**. |
| **B. Kho dữ liệu phiên bản ShakeMap cho phân tích vùng chịu rung ở Philippines**        | Catalog và ShakeMap có thể được cập nhật; khó truy vấn lịch sử phiên bản và so sánh mức rung theo event, vùng và chất lượng sản phẩm.                                              | Khác với ComCat/ShakeMap ở chỗ lưu version, provenance và event-to-region facts. Tuy nhiên đã có paper earthquake warehouse gần đây nên tính mới yếu hơn.                 | USGS ComCat, ShakeMap Atlas, SRTM. Công khai và dễ tải theo event.                                    | So sánh thời gian truy vấn event-centric với bảng phẳng; đo số event có ShakeMap, thay đổi intensity giữa phiên bản, coverage và completeness.                                 | Dễ làm nhất về dữ liệu, nhưng khó bảo vệ tính mới. Khối lượng **khả thi cao**, song cần tránh trùng paper 2026.                                                             |
| **C. Kho dữ liệu đánh giá độ đầy đủ hotspot cháy rừng ở một vùng Việt Nam**             | Hotspot bị ảnh hưởng bởi mây, lịch bay và độ phân giải; thống kê theo ngày/khu vực có thể bị hiểu sai nếu không lưu quality và coverage.                                           | FIRMS cung cấp dữ liệu hotspot; đề tài nghiên cứu cách warehouse biểu diễn coverage, confidence và missingness để tránh biến “không quan sát thấy” thành “không có cháy”. | NASA FIRMS, ERA5, SRTM, ESA WorldCover. Công khai; FIRMS có API/download.                             | Đo tỷ lệ coverage theo ngày, số hotspot theo confidence, thay đổi ranking khu vực khi lọc quality, tương quan trễ giữa gió/độ ẩm và hotspot.                                   | Dễ tải nhưng khó tạo ground truth cháy thật. Khối lượng **khả thi trung bình–cao**; phần kết luận phải giới hạn ở data quality, không tuyên bố phát hiện cháy chính xác.    |

## 5. Tự phản biện ứng viên mạnh nhất

### Đề xuất ban đầu

> Xây dựng kho dữ liệu tích hợp Sentinel-1, rainfall và DEM để giám sát ngập lụt Đồng bằng sông Cửu Long.

Đề xuất này vẫn quá rộng và dễ bị phản biện là “chỉ xây kho dữ liệu”.

### Phản biện của giảng viên

**“Khác gì GFM?”**

GFM đã có Sentinel-1 flood monitoring toàn cầu. Vì vậy, không được tuyên bố đề tài tạo ra hệ thống flood mapping tốt hơn GFM.

**“Nếu dữ liệu thiếu hoặc nhiễu thì sao?”**

Đó phải là một phần của research question, không phải vấn đề giấu đi. Warehouse cần lưu `quality_flag`, `missing_pixel_ratio`, `temporal_gap`, `source_timestamp` và `processing_version`.

**“Ai dùng warehouse và dùng để trả lời gì?”**

Đối tượng sử dụng là nhóm phân tích thiên tai hoặc sinh viên nghiên cứu vùng. Họ cần trả lời các câu hỏi tổng hợp:

- Sự kiện nào có diện tích ngập lớn nhất?
- Lượng mưa tích lũy 1–3 ngày trước event liên quan thế nào đến diện tích ngập?
- Kết quả có thay đổi khi chỉ dùng observation đạt quality threshold không?
- Khu vực nào có thống kê không đáng tin vì thiếu ảnh hoặc lệch thời gian?

### Phiên bản đã thu hẹp

> **Thiết kế và đánh giá kho dữ liệu chất lượng-aware cho tổng hợp sự kiện ngập từ Sentinel-1, GPM IMERG và SRTM tại một tiểu vùng Đồng bằng sông Cửu Long giai đoạn 2018–2024.**

Phạm vi nên khóa như sau:

- Không xây hệ thống cảnh báo thời gian thực.
- Không huấn luyện deep learning.
- Không tuyên bố tạo flood map tốt hơn GFM.
- Chỉ chọn một tiểu vùng, khoảng 5–10 sự kiện ngập.
- Sentinel-1 dùng để lấy flood extent hoặc statistics đã tiền xử lý.
- GPM IMERG dùng để tính rainfall window.
- SRTM dùng làm dimension/attribute địa hình.
- Đóng góp chính là schema, pipeline, quality/provenance model và thực nghiệm sensitivity.

Research question phù hợp:

> Việc biểu diễn chất lượng quan sát, dữ liệu thiếu và độ lệch thời gian trong kho dữ liệu ảnh hưởng thế nào đến độ đầy đủ và độ ổn định của các truy vấn tổng hợp sự kiện ngập?

Hypothesis:

> Warehouse có quality/provenance dimension giúp phát hiện các event có thống kê không đáng tin và làm thay đổi kết luận tổng hợp so với warehouse chỉ lưu giá trị ngập mà không lưu chất lượng.

## 6. Khuyến nghị cuối cùng

Tôi khuyến nghị khóa **Ứng viên A**, vì:

- **Khả thi nhất:** dữ liệu có API/catalog công khai, có thể cắt nhỏ theo vùng và chỉ lưu aggregate thay vì toàn bộ raster.
- **Tính mới vừa đủ và đúng hướng môn học:** không cạnh tranh trực tiếp với GFM ở bài toán flood mapping; tập trung vào quality-aware event warehouse.
- **Đo lường được:** có coverage ratio, missingness, temporal gap, ingestion latency, số lượng truy vấn và độ thay đổi của kết quả.
- **Dễ hoàn thành 13 bước:** bước 7–12 có thể dùng SQL warehouse, PostGIS/DuckDB, Python và một số bảng fact/dimension rõ ràng.
- **Ít rủi ro hơn earthquake:** hướng earthquake đã có paper rất gần về spatio-temporal data warehouse.
- **Ít phụ thuộc ground truth hơn wildfire:** không cần chứng minh “phát hiện cháy đúng”, chỉ cần đánh giá tính đầy đủ và ổn định của dữ liệu ngập.

Tên đề tài nên dùng khi trao đổi với Phụng:

> **Kho dữ liệu chất lượng-aware cho phân tích sự kiện ngập bằng dữ liệu Sentinel-1 và GPM tại một tiểu vùng Đồng bằng sông Cửu Long**

Đây là đề tài đủ hẹp để làm trong một học kỳ, nhưng vẫn có research question và phép đo rõ ràng thay vì chỉ “xây kho dữ liệu về ngập lụt”.
