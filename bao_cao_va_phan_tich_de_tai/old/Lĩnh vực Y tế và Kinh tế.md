## Kết luận nhanh

Có hai hướng đáng giữ lại:

1. **Y tế:** đối chiếu sai lệch giữa các nguồn số liệu tử vong công khai, có truy vết định nghĩa và phiên bản dữ liệu.
2. **Kinh tế:** đo ảnh hưởng của mã HS, dữ liệu mirror và cập nhật sửa đổi lên thống kê xuất nhập khẩu của Việt Nam.

Khuyến nghị sơ bộ: **chọn hướng y tế**, vì không cần dữ liệu bệnh nhân, không cần CITI/DUA, phạm vi nhỏ và giá trị của kho dữ liệu đo được trực tiếp bằng truy vấn đối chiếu.

Tính mới dưới đây được hiểu là “khe hở kỹ thuật có thể kiểm chứng”, không phải tuyên bố chắc chắn rằng chưa từng có paper nào làm. Trước khi khóa đề tài cần tìm kiếm thêm theo đúng bệnh, thời gian và schema.

---

# A. Domain y tế

## Bước 1 — Khảo sát có so sánh

| Nguồn                                                                                                                                | Dữ liệu và cách tổ chức                                                                                                    | Điểm còn bỏ sót                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| [MIMIC-IV](https://physionet.org/content/mimiciv/1.0/)                                                                               | Hồ sơ ICU của một bệnh viện, gồm bệnh án, xét nghiệm, thuốc, thủ thuật; dữ liệu quan hệ, đã de-identify                    | Đơn trung tâm, thiên về ICU; cần credentialing, CITI training và ký DUA                                                                      |
| [eICU-CRD](https://www.physionet.org/content/eicu-crd/2.0/)                                                                          | Hơn 200.000 ICU admissions từ 208 bệnh viện; nhiều bảng theo vital signs, lab, diagnosis, treatment                        | Các ICU không có cùng interface, nên “không có bản ghi” có thể là thiếu kết nối chứ không phải không có phép đo; cũng cần CITI/DUA           |
| [OMOP CDM/OHDSI](https://ohdsi.github.io/CommonDataModel/)                                                                           | Chuẩn hóa cấu trúc, mã bệnh, thuốc, thủ thuật và vocabulary qua ETL                                                        | Là chuẩn tổ chức chứ không phải một dataset hoàn chỉnh; không tự giải quyết missingness, sai khác nguồn hoặc mất ngữ cảnh nguồn              |
| [WHO GHO OData](https://www.who.int/data/gho/info/gho-odata-api) và [WHO Data Hub/xMart](https://data.who.int/about/data/whdh/xmart) | Kho chỉ số sức khỏe quốc gia/toàn cầu, API theo indicator, country, time và dimension; WHO đang chuyển sang Data Hub/xMart | Dữ liệu chủ yếu là aggregate; định nghĩa, mã cũ và lịch cập nhật có thể thay đổi. GHO OData cũ được ghi nhận sẽ deprecated sau cuối 2025     |
| [CDC WONDER](https://wonder.cdc.gov/wonder/help/wonder-api.html)                                                                     | Truy vấn mortality, birth, chronic disease và dữ liệu y tế công cộng; API trả summary table, kèm caveat và footnote        | Không cung cấp toàn bộ record-level data; nhiều API mortality chỉ cho truy vấn quốc gia; suppression và quy tắc công bố làm hạn chế chi tiết |
| [IHME GBD](https://ghdx.healthdata.org/gbd-2021/data-input-sources)                                                                  | Ước lượng deaths, DALYs, YLL, YLD theo cause, risk, age, sex, place, year, có uncertainty interval                         | Đây là estimate đã qua mô hình hóa, redistribution và smoothing, không phải raw registry; cần lưu rõ phiên bản và uncertainty                |
| [Our World in Data Grapher](https://ourworldindata.org/grapher/life-expectancy)                                                      | Chuẩn hóa nhiều nguồn thành CSV/JSON, có metadata và biểu đồ                                                               | Thuận tiện để dùng lại nhưng là lớp xử lý trung gian; cần truy ngược provider gốc, license, ngày cập nhật và quy tắc biến đổi                |

Các hệ thống clinical warehouse thường tập trung vào chuẩn hóa và phân tích dữ liệu bệnh nhân. Ngược lại, WHO, CDC WONDER và GBD cung cấp các số liệu aggregate nhưng theo định nghĩa, quy trình và mức độ mô hình hóa khác nhau. [OMOP cũng thừa nhận không có một nguồn quan sát đơn lẻ nào đủ toàn diện cho mọi câu hỏi nghiên cứu](https://ohdsi.github.io/CommonDataModel/background.html).

Một paper gần đây đã so sánh trực tiếp CDC WONDER với GBD cho tử vong tim mạch và cho thấy xu hướng tương tự nhưng độ lớn khác nhau. Vì vậy, đề tài không nên tuyên bố “phát hiện mới rằng hai nguồn có số khác nhau”; khe hở phù hợp hơn là **xây cơ chế truy vết, tái lập và giải thích sai lệch**. [Paper so sánh CDC WONDER–GBD](https://academic.oup.com/aje/advance-article/doi/10.1093/aje/kwag153/8728047)

## Bước 2 — Bản đồ nghiên cứu

Ký hiệu: ● nhiều, ◐ vừa, ○ còn thưa.

| Loại dữ liệu/vấn đề            | Tích hợp nguồn | Chuẩn hóa mã | Cập nhật/phiên bản | Chất lượng/thiếu dữ liệu | Thời gian–không gian–dân số |
| ------------------------------ | -------------: | -----------: | -----------------: | -----------------------: | --------------------------: |
| Hồ sơ lâm sàng/ICU             |              ◐ |            ● |                  ◐ |                        ● |                           ◐ |
| Bệnh truyền nhiễm/surveillance |              ◐ |            ◐ |                  ● |                        ◐ |                           ● |
| Bệnh mạn tính/tử vong          |              ○ |            ◐ |                  ◐ |                        ◐ |                           ● |
| Chỉ số y tế công cộng          |              ○ |            ◐ |                  ○ |                        ● |                           ● |
| So sánh estimate với registry  |              ○ |            ◐ |                  ○ |                        ● |                           ◐ |

Những hướng đã được làm khá nhiều:

- OMOP/CDM, chuẩn hóa mã bệnh và ETL hồ sơ lâm sàng.
- Dự đoán trên MIMIC/eICU.
- Dashboard và truy vấn một nguồn dữ liệu.

Những ô còn thưa hơn:

- Theo dõi **cùng một chỉ số nhưng khác nguồn, khác định nghĩa, khác phiên bản**.
- Đo riêng ảnh hưởng của missingness, suppression, redistribution và uncertainty.
- Kho dữ liệu có thể trả lời: “con số này khác con số kia bao nhiêu và vì sao?”

## Bước 3–4 — Ba khoảng trống và đề tài ứng viên

| Ứng viên                                                                                                                                       | Vấn đề Y và khác gì Z                                                                                                                                                                                                                     | Dữ liệu công khai                                                                                                                                                        | Cách đo W                                                                                                                                                                                                                                       | Rủi ro và khối lượng                                                                                                                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **H1 — “Cùng một bệnh thận mạn nhưng số tử vong không giống nhau — kho dữ liệu truy vết sai lệch giữa CDC WONDER và GBD tại Hoa Kỳ”**          | CDC WONDER dựa trên death certificate và ICD-10; GBD là estimate có redistribution/modeling. Các paper hiện có đã so sánh CVD/diabetes, nhưng chưa biến câu hỏi thành warehouse có lineage, snapshot và audit query cho một nhóm bệnh hẹp | CDC WONDER có mã CKD N18 và dữ liệu theo năm, tuổi, giới, chủng tộc, địa lý. GBD Results có cause-specific estimates 1990–2021. Không có định danh; không cần MIMIC/CITI | Star schema gồm `fact_mortality`, `dim_source`, `dim_cause`, `dim_time`, `dim_population`, `dim_definition`, `dim_version`. Đo relative difference, absolute difference, trend agreement, overlap CI/UI, completeness và khả năng tái lập query | Cần pilot xác nhận mapping CKD trong GBD khớp đủ với N18; nếu không, thu hẹp thành “chronic kidney disease/renal failure category”. **Khối lượng: vừa, khoảng 10–12 tuần; phù hợp 2 người** |
| **H2 — “Một phép đo ICU biến mất ở bệnh viện này nhưng không biến mất ở bệnh viện kia — kho dữ liệu đo missingness sau chuẩn hóa MIMIC–eICU”** | OMOP chuẩn hóa cấu trúc/mã nhưng không chứng minh rằng hai nguồn có mức độ quan sát tương đương. Khác với các paper chỉ dùng MIMIC/eICU để train model: đề tài đo ảnh hưởng của interface và missingness lên truy vấn warehouse           | MIMIC-IV và eICU-CRD đều de-identified. Tuy nhiên cần credentialed access, CITI training và DUA; eICU demo có thể dùng làm fallback ban đầu                              | Chuẩn hóa một syndrome hẹp, ví dụ sepsis hoặc respiratory failure. Đo coverage theo biến, time-to-first-measurement, missingness theo ICU, consistency sau ETL và kết quả truy vấn trước/sau chuẩn hóa                                          | Rủi ro access chậm, schema lớn, hai người dễ quá tải. **Khối lượng: cao, 13–16 tuần; chỉ nên chọn nếu đã có quyền truy cập**                                                                |
| **H3 — “Cùng một chỉ số sức khỏe nhưng khác ngày cập nhật và khác mô tả — kho dữ liệu theo dõi metadata drift giữa WHO và OWID”**              | WHO Data Hub là nguồn chính thức; OWID cung cấp lớp xử lý và phân phối thuận tiện. Khe hở là đo update lag, thay đổi định nghĩa, thay đổi mã và khả năng tái lập snapshot cho một nhóm nhỏ indicator                                      | WHO Data Hub/xMart và OWID CSV/metadata. Aggregate, không định danh, không cần CITI                                                                                      | Chọn 3–5 indicator, ví dụ life expectancy hoặc child mortality, trong 20–30 quốc gia. Đo update lag, missingness, metadata mismatch, value drift và reproducibility bằng hash/snapshot                                                          | Không tạo ra phát hiện y khoa; tính mới thiên về data engineering. **Khối lượng: thấp–vừa, 8–10 tuần**                                                                                      |

## Bước 5 — Tự phản biện H1

**Phản biện:** “So sánh CDC WONDER và GBD đã có paper. Vậy đề tài khác gì?”

**Trả lời:** Không lặp lại một phân tích dịch tễ học tổng quát. Đề tài chỉ chọn một nhóm bệnh hẹp và đóng góp ở:

- lưu đồng thời giá trị, định nghĩa, mã nguyên nhân, population denominator, source, version và query parameters;
- tái chạy đúng một truy vấn từ snapshot đã lưu;
- phân rã sai lệch thành khác biệt định nghĩa, khác biệt nguồn, uncertainty và xử lý dữ liệu;
- công bố schema và bộ test chất lượng, không tuyên bố nguyên nhân tử vong “thật” hơn nguồn kia.

**Phản biện:** “Nếu GBD không có đúng nhóm CKD tương ứng với ICD-10 N18 thì sao?”

**Trả lời:** Kiểm tra ngay trong pilot. Nếu không mapping được, thay bằng category rộng hơn đã xuất hiện ở cả hai nguồn, hoặc loại H1. Không gộp mã tùy ý.

**Phản biện:** “Ai dùng kho này?”

**Trả lời:** Người phân tích y tế công cộng hoặc sinh viên cần biết một con số tử vong có thể so sánh được đến mức nào. Câu hỏi cụ thể là:

> “Trong giai đoạn 1999–2021, số tử vong và mortality rate của cùng một nhóm bệnh lệch bao nhiêu giữa hai nguồn, và sự lệch đó có ổn định theo thời gian/nhóm dân số không?”

### H1 sau khi thu hẹp

**Research question:** Sau khi chuẩn hóa năm, đơn vị, dân số và nhóm bệnh, sai lệch giữa CDC WONDER và GBD là bao nhiêu; xu hướng có đồng nhất không?

**Hypothesis:** Hai nguồn có thể cùng chỉ ra xu hướng dài hạn nhưng vẫn có sai lệch có hệ thống về độ lớn, đặc biệt khi định nghĩa và phương pháp xử lý nguyên nhân tử vong khác nhau.

**Đóng góp:** Một warehouse có lineage và snapshot giúp tái lập, kiểm toán và giải thích sự khác biệt giữa hai nguồn aggregate công khai.

---

# B. Domain kinh tế

## Bước 1 — Khảo sát có so sánh

| Nguồn                                                                                                                                      | Dữ liệu và cách tổ chức                                                                                                  | Điểm còn bỏ sót                                                                                                                     |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| [World Bank Indicators API](https://datahelpdesk.worldbank.org/knowledgebase/articles/889392)                                              | Gần 16.000 time series, truy vấn theo quốc gia, indicator, năm/tháng/quý; API không cần API key                          | Phần lớn người dùng thấy phiên bản hiện tại; không phải indicator nào cũng có lịch sử release/vintage dễ truy vấn                   |
| [IMF Data API](https://data.imf.org/en/Resource-Pages/IMF-API)                                                                             | SDMX 2.1/3.0, nhiều dataset vĩ mô và tài chính                                                                           | Mã dimension phức tạp; cùng tên chỉ tiêu có thể khác sector, unit, valuation hoặc forecast convention                               |
| [IMF WEO](https://data.imf.org/Datasets/WEO)                                                                                               | GDP, inflation, unemployment, fiscal, trade và projections; có current release, historical forecasts và tài liệu vintage | Có revision và forecast; nếu không lưu release/vintage thì kết quả nghiên cứu sau này khó tái lập                                   |
| [FRED/ALFRED](https://alfred.stlouisfed.org/help)                                                                                          | FRED hiển thị phiên bản mới nhất; ALFRED lưu vintage theo thời điểm phát hành                                            | Mạnh cho dữ liệu Mỹ; không tự giải quyết crosswalk giữa nhiều cơ quan hoặc quốc gia                                                 |
| [OECD Data API](https://www.oecd.org/en/data/insights/data-explainers/2024/09/api.html)                                                    | SDMX, có structure, codelist, data và một số dataset revision                                                            | Nhiều dimension và quy tắc OECD; khả năng so sánh phụ thuộc định nghĩa quốc gia                                                     |
| [Eurostat SDMX API](https://ec.europa.eu/eurostat/web/user-guides/data-browser/api-data-access/api-detailed-guidelines/sdmx2-1/data-query) | API truy vấn dữ liệu và metadata theo dimensions                                                                         | Eurostat ghi rõ hệ thống chính chỉ giữ phiên bản cuối, giá trị cũ bị mất; khó tái lập “what was known at the time”                  |
| [UN Comtrade/WITS](https://uncomtrade.org/docs/un-comtrade-api/) và [WITS API](https://wits.worldbank.org/witsapiintro.aspx?lang=en)       | Trade theo reporter, partner, product, flow, period, HS/SITC; WITS cung cấp lớp truy vấn và chỉ số thương mại            | Comtrade có thể revise dữ liệu nhưng chỉ giữ một phiên bản hiện tại; tồn tại mirror asymmetry, khác hệ thống hải quan và khác mã HS |

UN Comtrade xác nhận rằng dữ liệu có thể được sửa nhưng không lưu archive nhiều phiên bản. Đây là một khe hở rõ cho warehouse có snapshot và lineage. [UN Comtrade revision policy](https://uncomtrade.org/docs/data-availability/)

## Bước 2 — Bản đồ nghiên cứu

| Loại dữ liệu/vấn đề | Tích hợp nguồn | Đơn vị/kỳ báo cáo | Revision/vintage | Chất lượng/thiếu dữ liệu | Thời gian–không gian |
| ------------------- | -------------: | ----------------: | ---------------: | -----------------------: | -------------------: |
| Vĩ mô/GDP           |              ● |                 ● |                ● |                        ◐ |                    ● |
| Thương mại          |              ◐ |                 ● |                ◐ |                        ● |                    ● |
| Lao động            |              ◐ |                 ● |                ◐ |                        ● |                    ◐ |
| Giá cả/lạm phát     |              ◐ |                 ● |                ◐ |                        ◐ |                    ● |
| Tài chính công/nợ   |              ◐ |                 ● |                ● |                        ◐ |                    ● |

Các hướng đã tương đối dày:

- API và dashboard cho từng nhà cung cấp.
- Forecasting từ GDP, CPI, unemployment.
- Chuẩn hóa SDMX ở cấp hệ thống.

Các ô còn thưa hơn:

- Đối chiếu **giá trị mới nhất với giá trị đã từng được công bố**.
- Lưu semantic crosswalk: cùng tên nhưng khác unit, sector, frequency hoặc valuation.
- Đo tác động của HS conversion, mirror trade và missing reporter lên một chuỗi thương mại cụ thể.

## Bước 3–4 — Ba khoảng trống và đề tài ứng viên

| Ứng viên                                                                                                                                   | Vấn đề Y và khác gì Z                                                                                                                                                                                                     | Dữ liệu công khai                                                                                                                                                                 | Cách đo W                                                                                                                                                                          | Rủi ro và khối lượng                                                                                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1 — “GDP công bố lần đầu đã thay đổi bao nhiêu — kho dữ liệu vintage cho một nhóm nước ASEAN”**                                         | IMF WEO và ALFRED đã cung cấp cơ chế vintage riêng. Khe hở không phải xây lại ALFRED, mà là tạo warehouse nhỏ để hỏi: dùng số liệu tại thời điểm công bố hay số liệu đã revision thì kết luận/mô hình thay đổi bao nhiêu  | IMF WEO current release, historical forecasts/vintages và World Bank WDI. Public download/API; WDI API không cần key                                                              | `fact_observation` có `observation_period`, `release_date`, `vintage`, `source`, `unit`, `forecast_flag`. Đo revision magnitude, sign change, forecast error và khác biệt backtest | IMF WEO có quy tắc release/vintage phức tạp. **Khối lượng: vừa, 9–11 tuần**                                                                             |
| **E2 — “Một lô hàng điện tử xuất khẩu và nhập khẩu không cho cùng một con số — kho dữ liệu đối chiếu mirror trade và mã HS của Việt Nam”** | UN Comtrade đã có mirror comparison và classification conversion. Khe hở là đo có kiểm soát việc HS edition, reporter/partner, FOB/CIF, missingness và revision làm thay đổi chuỗi xuất khẩu điện tử của Việt Nam thế nào | UN Comtrade, WITS/UN Comtrade metadata; API preview/free có thể dùng, bulk/unattended extraction có giới hạn                                                                      | Scope: Việt Nam, nhóm HS 85, 5 đối tác, 2015–2024. Đo mirror asymmetry ratio, tác động HS conversion, coverage, missingness và độ ổn định sau cập nhật                             | Comtrade/WITS không phải hai nguồn độc lập hoàn toàn; cần nói rõ đây là audit nội bộ của cùng hệ sinh thái dữ liệu. **Khối lượng: vừa–cao, 10–12 tuần** |
| **E3 — “Tỷ lệ thất nghiệp quốc gia và tỷ lệ mô hình hóa lệch nhau bao nhiêu — kho dữ liệu đối chiếu lao động trẻ ở ASEAN”**                | World Bank phổ biến cả national estimate và modeled ILO estimate; ILOSTAT giữ metadata chi tiết. Khe hở là lưu hai loại quan sát cùng schema và đo khi nào chúng cho kết luận khác nhau                                   | World Bank WDI và [ILOSTAT SDMX API](https://www.ilo.org/sites/default/files/2024-12/ILOSTAT-SDMX_Dissem%20API%20Ref%20Guide_V4.1-%28ILO%20Style%29.pdf). Public, không định danh | Chọn nhóm 15–24 tuổi, 6 nước ASEAN, 2010–2025. Đo chênh lệch national–modeled, missingness, update lag và sensitivity của xếp hạng quốc gia                                        | Tính mới thấp hơn; phải kiểm tra national estimate có đủ dài cho từng nước. **Khối lượng: thấp–vừa, 8–10 tuần**                                         |

## Bước 5 — Tự phản biện E2

**Phản biện:** “UN Comtrade đã có mirror comparison và conversion rồi. Đề tài có gì mới?”

**Trả lời:** Không tuyên bố xây công cụ thay thế Comtrade. Đề tài chỉ kiểm chứng một câu hỏi hẹp:

> “Với nhóm HS 85 của Việt Nam và một số đối tác, phần trăm sai lệch mirror và tác động của HS edition conversion thay đổi thế nào theo năm?”

Đóng góp là:

- một schema lưu cả reporter flow và mirror flow;
- giữ mã gốc, mã chuyển đổi, edition, unit, valuation và thời điểm tải;
- chạy ablation: raw HS code, converted HS code, loại/bỏ năm thiếu;
- chứng minh bằng query rằng cùng một câu hỏi có thể cho kết quả khác tùy cách chuẩn hóa.

**Phản biện:** “Nếu dữ liệu thiếu hoặc đối tác không báo cáo đầy đủ thì sao?”

**Trả lời:** Chọn trước 5 đối tác có coverage ổn định; không nội suy số liệu bị thiếu. Missingness là một kết quả, không được che bằng zero.

**Phản biện:** “Ai dùng kho này?”

**Trả lời:** Người phân tích thương mại cần biết một con số xuất khẩu là giá trị do Việt Nam báo cáo, hay giá trị nhập khẩu do đối tác báo cáo, và hai con số lệch nhau đến đâu.

### E2 sau khi thu hẹp

**Research question:** Trong giai đoạn 2015–2024, với HS 85 và 5 đối tác chính, mirror asymmetry của Việt Nam thay đổi thế nào sau khi kiểm soát HS edition, flow, valuation và missingness?

**Hypothesis:** Một phần đáng kể biến động chuỗi thương mại không đến từ thay đổi kinh tế thật mà đến từ classification, reporting coverage và revision.

**Đóng góp:** Warehouse thương mại có thể giải thích nguồn gốc của mỗi observation và tái tạo lại phép tính asymmetry từ snapshot cụ thể.

---

# So sánh ba ứng viên mạnh nhất

| Tiêu chí                             |                                       H1 y tế |               E2 thương mại | E3 lao động |
| ------------------------------------ | --------------------------------------------: | --------------------------: | ----------: |
| Dữ liệu dễ tiếp cận                  |                                           Cao |                     Cao–vừa |         Cao |
| Cần dữ liệu định danh/IRB            |                                         Không |                       Không |       Không |
| Độ rõ của khe hở                     | Cao nếu tập trung vào lineage/reproducibility |                         Cao |         Vừa |
| Tính mới kỹ thuật                    |                                       Vừa–cao |                     Vừa–cao |         Vừa |
| Độ phức tạp ETL                      |                                           Vừa |        Cao hơn do HS/mirror |    Thấp–vừa |
| Khả năng chứng minh giá trị bằng SQL |                                       Rất cao |                     Rất cao |         Cao |
| Rủi ro bị phản biện “đã có rồi”      |                Vừa, vì đã có paper comparison | Vừa, vì Comtrade đã có tool |     Cao hơn |
| Khả năng hoàn thành 13 bước          |                                           Cao |      Cao nếu giới hạn scope |         Cao |

## Khuyến nghị khóa đề tài

### Khuyến nghị số 1

**“Cùng một bệnh thận mạn nhưng số tử vong không giống nhau — kho dữ liệu truy vết và đo độ lệch giữa CDC WONDER và GBD tại Hoa Kỳ, 1999–2021.”**

Đề tài này thắng vì:

- không cần dữ liệu bệnh nhân hoặc quyền truy cập MIMIC/eICU;
- nguồn dữ liệu aggregate, có thể tải và truy vấn lại;
- vấn đề không phải “xây kho dữ liệu y tế” chung chung mà là kiểm tra một hiện tượng cụ thể: **cùng nhóm bệnh nhưng khác nguồn cho ra số khác nhau**;
- có thể đo bằng SQL, data-quality tests, discrepancy metrics và snapshot reproducibility;
- phù hợp với hai người trong một học kỳ nếu không mở rộng sang dự đoán, causal inference hoặc toàn bộ bệnh tật.

### Khuyến nghị số 2 nếu chọn kinh tế

**“Một lô hàng điện tử xuất khẩu và nhập khẩu không cho cùng một con số — kho dữ liệu đối chiếu mirror trade và mã HS của Việt Nam, 2015–2024.”**

Đây là lựa chọn kinh tế tốt hơn các đề tài “dự báo GDP” chung chung vì vấn đề nằm ngay trong dữ liệu thương mại: mã phân loại, flow, reporter/partner, missingness và revision.

## Pilot bắt buộc trước khi lock

Trong 3–5 ngày, hai bạn nên kiểm tra:

1. Tải được một mẫu dữ liệu thật từ từng nguồn.
2. Xác nhận cùng một indicator/cause có thể mapping được.
3. Đếm số năm, số nhóm dân số và số địa lý còn đủ dữ liệu.
4. Chạy thử một query discrepancy.
5. Lưu metadata, ngày tải, phiên bản và checksum.
6. Tìm thêm paper theo đúng scope hẹp để kiểm tra novelty.

Nếu H1 không mapping được nhóm bệnh CKD giữa CDC WONDER và GBD, nên chuyển sang **H3** thay vì cố gộp mã thủ công.
