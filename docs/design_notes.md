# TuringLab Bölüm 2 Tasarım Notları

## TM-1: Unary -> Binary Çevirici

Stratejim unary girdiyi iki `X` işaretçisi arasına almak ve sol `X` işaretçisinin solunda bir ikili sayaç tutmak oldu. Her turda iki `X` arasındaki ilk `1` siliniyor, sonra sayaç bir artırılıyor. Tüm `1` sembolleri bitince iki işaretçi temizleniyor ve bantta yalnızca ikili sayaç kalıyor. Boş unary girdiyi kenar durum olarak boş çıktı ile bıraktım; testte de bu davranışı açıkça kontrol ediyorum.

Bu makinede 8 durum kullandım. Daha az durumla yazmak mümkün olabilir, ama `q_find`, `q_inc` ve `q_cleanup_left` gibi görevleri ayırmak geçiş tablosunu daha okunabilir yaptı. Şerit alfabesi el kitabındaki `{1, 0, B, X}` sınırına uyar. En kritik karar, sayacı sol tarafta tutmaktı; böylece ikili sayı büyürken sola doğru genişleyebiliyor ve araya sembol ekleme problemi çıkmıyor. Her unary `1` için bantta birkaç kez ileri geri gidildiği için yaklaşık `O(n^2)` adımda biter. En çok zorlandığım bug sayaç yönüydü: sayacı sağ tarafta tutunca taşma durumunda başa bit eklemek gerekiyordu. Sayacı sol `X` işaretçisinin soluna alınca bu sorun kayboldu.

## TM-2: Binary Compare

Bu makine `w1#w2` biçiminde iki normalize ikili sayıyı karşılaştırır; başında gereksiz sıfırlar olmayan girdiler için tasarlandı. Önce uzunlukları karşılaştırıyorum: soldaki her bit `A/C`, sağdaki karşılığı `D/E` ile işaretleniyor. Sol taraf erken biterse sağda işaretsiz bit kalıp kalmadığına bakılıyor. Uzunluklar farklıysa sonuç doğrudan belli; eşitse işaretler geri alınıp soldan sağa ilk farklı bit aranıyor.

16 durum kullandım, çünkü uzunluk karşılaştırması ve leksikografik karşılaştırmayı tek tabloda karıştırmak geçişleri çok hataya açık hale getiriyordu. `A/C` soldaki `0/1`, `D/E` sağdaki `0/1` için kullanıldı; böylece işaretleme sırasında bilgi kaybolmadı. Karmaşıklık tek şeritli yapı yüzünden `O(n^2)`: her eşleştirme için bant başına dönülüyor. En zor bug, aynı durumda hem soldaki `0`ı taramak hem sağdaki `0`ı işaretlemek istememdi; deterministik TM'de aynı `(state, read)` için iki geçiş olamayınca `q_seek_hash` ve `q_mark_second` durumlarını ayırdım.

## TM-3: String Copy

Kopyalama makinesi önce girdinin sonuna `#` koyuyor. Sonra sol bölümdeki ilk işlenmemiş `a` veya `b` sembolünü sırasıyla `A` veya `C` ile işaretliyor, bandın en sağına gidip aynı sembolü ekliyor ve başa dönüyor. Sol bölüm tamamen işaretlenince `A/C` sembolleri tekrar `a/b` yapılıyor. Son bant biçimi `w#w` oluyor.

7 durum yeterli oldu; çünkü işin doğal evreleri zaten belirgin: sona git, başa dön, işaretle, `a` ekle, `b` ekle, geri yükle, kabul et. Şerit alfabesinde `C` sembolünü `b` işaretçisi olarak kullandım; el kitabındaki `B'` fikrine karşılık geliyor ama YAML içinde daha sade. Karmaşıklık `O(n^2)`, çünkü her karakter kopyalandığında bant sonuna gidilip geri dönülüyor. Hata ayıklamada en çok boş girdiyi düşündüm: boş girdinin sonucu `#` olmalı, çünkü `w#w` formülünde `w = ε` için ayraç yine görünür kalıyor.

## TM-4: Binary Divisible by 4

Öğrenci seçimi olarak ikili girdinin 4'e bölünebilirliğini seçtim. Normalize ikili sayılarda 4'e bölünebilmek için sayı `0` olmalı veya son iki biti `00` olmalı. Bu nedenle bu makine aslında bant üzerinde sağa doğru ilerleyen küçük bir DFA gibi çalışıyor: son görülen bitleri durumlarda tutuyor ve boş sembole gelince kabul/ret kararını veriyor.

8 durum kullandım. Daha az durumla yapılabilir, ama `q_single0`, `q_last0`, `q_last1` ve `q_suffix00` durumları kuralı açık gösteriyor. Ek işaretçi sembole gerek olmadığı için alfabe yalnızca `{0, 1, B}`. Karmaşıklık `O(n)`; bant baştan sona bir kez okunuyor. En önemli hata ayıklama noktası `0` ve `10` girdilerini ayırmaktı. Teorik olarak 0, 4'e bölünür; bu yüzden `0` kabul ediliyor, `10` ve boş girdi reddediliyor.
