
🔗 GOOGLE DRIVE FILE ID ALMA KILAVUZU
===================================

Google Drive'daki her klasör için File ID alması gerekiyor:

1. Google Drive'ı açın: https://drive.google.com/drive/u/6/folders/13CBL3-czwwxim49iz6NZ8t8Eq42YeyaW

2. Her klasöre sağ tıklayın → "Paylaş"

3. "Erişim" kısmında "Kısıtlı" yerine "Linki olan herkes" seçin

4. "Linki kopyala" butonuna tıklayın

5. Kopyalanan linkten File ID'sini alın:

   Örnek link: https://drive.google.com/drive/folders/1abc123def456ghi789jkl?usp=sharing
   File ID: 1abc123def456ghi789jkl

6. Aşağıdaki klasörler için bu işlemi yapın:


   📁 1_CODES
      Açıklama: Core kod modülleri
      Link: [Buraya Google Drive linkini yapıştırın]
      File ID: [Buraya File ID'yi yazın]

   📁 4_MODELS
      Açıklama: YOLO model dosyaları
      Link: [Buraya Google Drive linkini yapıştırın]
      File ID: [Buraya File ID'yi yazın]

   📁 5_TİCKET_DATA
      Açıklama: 1,814 frame dataset
      Link: [Buraya Google Drive linkini yapıştırın]
      File ID: [Buraya File ID'yi yazın]

   📁 9_TICKETv2
      Açıklama: 5,354 frame dataset (ana)
      Link: [Buraya Google Drive linkini yapıştırın]
      File ID: [Buraya File ID'yi yazın]


7. File ID'leri aldıktan sonra, aşağıdaki dosyayı güncelleyin:
   8_TRAINING/vast_ai_setup/gdrive_config.py

8. DATASET_FOLDERS dictionary'sindeki YOUR_*_ID kısımlarını gerçek ID'lerle değiştirin.

ÖRNEK:
------
"5_TİCKET_DATA": {
    "id": "1abc123def456ghi789jkl",  # ← Buraya gerçek ID
    "local_path": "5_TİCKET_DATA",
    "sync": False
},
