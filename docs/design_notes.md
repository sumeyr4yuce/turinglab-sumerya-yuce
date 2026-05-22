# TuringLab Bölüm 2 Tasarım Notları

Her makine için el kitabının sayfa 13'te istediği beş soruyu sırasıyla yanıtlıyorum:
strateji, durum sayısı, şerit alfabesi seçimi, karmaşıklık ve hata ayıklama hikayesi.

## TM-1: Unary -> Binary Çevirici

1. **Strateji.** Unary girdiyi iki `X` işaretçisi arasına alıyorum ve sol `X` işaretçisinin solunda bir ikili sayaç tutuyorum. Her turda iki `X` arasındaki ilk `1` siliniyor, sayaç bir artırılıyor. Tüm `1`'ler tüketildiğinde iki işaretçi temizleniyor ve bantta yalnızca ikili sayaç kalıyor. Boş unary girdiyi kenar durum olarak boş çıktı ile bıraktım.

2. **Durum sayısı.** 8 durum kullandım. Daha az durumla yazmak mümkün olabilir, ama `q_find`, `q_inc`, `q_cleanup_left` gibi görevleri ayrı tutmak geçiş tablosunu okunabilir yaptı; 5-6 duruma sıkıştırmak için aynı durumda hem arama hem güncelleme yapmak gerekirdi, bu da hata olasılığını artırırdı.

3. **Şerit alfabesi seçimi.** El kitabındaki `{1, 0, B, X}` sınırına birebir uydum. Yalnızca tek bir yardımcı sembol (`X`) yetti çünkü işaretleyici görevini iki `X` arasındaki bölgeyi tanımlamak için kullandım; ikinci bir yardımcıya gerek kalmadı.

4. **Karmaşıklık.** Her unary `1` için bantta birkaç kez ileri-geri gidiliyor, bu da yaklaşık `O(n^2)` adımda biter — n unary girdinin uzunluğu.

5. **Hata ayıklama hikayesi.** En çok zorlandığım yer sayacın yönüydü. Sayacı sağ tarafta tutunca taşma durumunda başa bit eklemek gerekiyordu, geçişler hızla karışıyordu. Sayacı sol `X` işaretçisinin soluna alınca sorun kayboldu çünkü ikili sayı doğal olarak sola doğru genişleyebiliyor.

## TM-2: Binary Compare

1. **Strateji.** `w1#w2` biçimindeki iki normalize ikili sayıyı karşılaştırıyorum; başında gereksiz sıfırlar olmayan girdiler için tasarlandı. Önce uzunlukları eşliyorum — soldaki her bit `A/C`, sağdaki karşılığı `D/E` ile işaretleniyor. Sol erken biterse sağda işaretsiz bit kalıp kalmadığına bakılıyor. Uzunluklar farklıysa sonuç doğrudan belli; eşitse işaretler geri alınıp soldan sağa ilk farklı bit aranıyor.

2. **Durum sayısı.** 16 durum kullandım. Uzunluk karşılaştırması ve leksikografik karşılaştırmayı tek tabloda karıştırmak deterministik TM kurallarını çok hataya açık hale getiriyordu; iki fazı `q_len_*` ve `q_cmp_*` ailelerine ayırınca her geçiş tek bir iş yapıyor. Daha azla yazılabilir ama okunabilirlik bozulurdu.

3. **Şerit alfabesi seçimi.** `A/C` soldaki `0/1` için, `D/E` sağdaki `0/1` için kullanıldı. Tek tip işaretleyici (örneğin sadece `X`) kullansaydım, eşit uzunluklarda işaretleri geri alıp bitleri orijinal değerine döndüremezdim — yani 4 ayrı işaretleyici sembol bilgi kaybı olmasın diye seçildi.

4. **Karmaşıklık.** Tek şeritli yapı nedeniyle `O(n^2)`: her bit eşleştirmesi için bant başına dönülüyor. (El kitabının pedagojik notunda da belirtildiği gibi, 2 şeritle bu doğrusala düşerdi.)

5. **Hata ayıklama hikayesi.** En zor bug, aynı durumda hem soldaki `0`ı taramak hem sağdaki `0`ı işaretlemek istememdi; deterministik TM'de aynı `(state, read)` için iki geçiş olamayacağı için `_validate` hata fırlattı. Çözüm: `q_seek_hash` ve `q_mark_second` durumlarını ayırmak.

## TM-3: String Copy

1. **Strateji.** Önce girdinin sonuna `#` koyuyorum. Sonra sol bölümdeki ilk işlenmemiş `a` veya `b` sembolünü sırasıyla `A` veya `C` ile işaretleyip bandın en sağına gidip aynı sembolü ekliyorum ve başa dönüyorum. Sol bölüm tamamen işaretlenince `A/C` sembolleri tekrar `a/b` yapılıyor. Son bant biçimi `w#w`.

2. **Durum sayısı.** 7 durum yeterli oldu çünkü işin doğal evreleri zaten belirgin: sona git, başa dön, işaretle, `a` ekle, `b` ekle, geri yükle, kabul et. Bunları aynı duruma sıkıştırmaya kalksam (örneğin `a` ve `b` için tek `q_append`), hangi sembolün ekleneceğini hatırlatacak bir bilgi taşımak gerekirdi.

3. **Şerit alfabesi seçimi.** El kitabındaki `{a, b, B, #, A, B'}` öneriler listesindeki `B'` yerine `C` kullandım — YAML'da tırnak sorunsuz olduğu ve `B` blank'ı ile karışmadığı için. Anlamı aynı: `A` işaretlenmiş `a`, `C` işaretlenmiş `b`.

4. **Karmaşıklık.** `O(n^2)`. Her karakter kopyalandığında bant sonuna gidilip geri dönülüyor, yani her bir karakter için `O(n)` iş.

5. **Hata ayıklama hikayesi.** En çok düşündürten kenar durumu boş girdiydi. Boş girdinin sonucu `#` olmalı çünkü `w#w` formülünde `w = ε` için ayraç yine görünür kalıyor. İlk yazımda boş girdiyi `q_accept`'e götüren bir kural yoktu, makine `no_transition` ile düşüyordu; `q_seek_end` durumuna `read: B, write: #, move L` kuralını ekleyince problem çözüldü.

## TM-4: Binary Divisible by 4 (Öğrenci Seçimi)

1. **Strateji.** İkili girdinin 4'e bölünebilirliğini test ediyorum. Normalize ikili sayılarda 4'e bölünebilmek için sayı `0` olmalı veya son iki biti `00` olmalı. Bu nedenle makine aslında bant üzerinde sağa doğru ilerleyen küçük bir DFA gibi çalışıyor: son görülen bitleri durumlarda tutuyor ve boş sembole gelince kabul/ret kararını veriyor.

2. **Durum sayısı.** 8 durum kullandım. Daha az durumla yapılabilir (teorik minimum 4-5 civarı) ama `q_single0`, `q_seen_one`, `q_last0`, `q_last1`, `q_suffix00` durumları kuralı açık gösteriyor ve hangi son ekleri ayırt etmem gerektiğini netleştiriyor.

3. **Şerit alfabesi seçimi.** Ek işaretçi sembole gerek olmadığı için alfabe yalnızca `{0, 1, B}`. Bilgiyi şerit yerine durumda taşıyorum — bu TM'in DFA benzeri yapısı zaten alfabe genişletmesini gereksiz kılıyor.

4. **Karmaşıklık.** `O(n)`. Bant baştan sona bir kez okunuyor, geri dönüş yok.

5. **Hata ayıklama hikayesi.** En önemli hata ayıklama noktası `0` ve `10` girdilerini ayırmaktı. Teorik olarak 0 sayısı 4'e bölünür; bu yüzden `0` kabul, `10` ve boş girdi ret. İlk denemede `q_start` üzerinden `0` okuduğumda doğrudan kabul durumuna sapıyordum, ama bu `10` girdisinde bandın ilk karakterini gördükten sonra hemen kabul anlamına gelirdi. `q_single0` ayrı bir durum olarak ekleyince "yalnızca tek `0` görüldü" senaryosu net ayrıldı.
