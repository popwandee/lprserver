# LPRServer

AI Camera Research Project สำหรับระบบตรวจจับป้ายทะเบียน

## วิธีเริ่มต้นใช้งาน

1. **Clone repo**
    ```bash
    git clone https://github.com/popwandee/lprserver.git
    cd lprserver
    ```

2. **ตั้งค่า environment**
    - สร้างไฟล์ `.env`, `.env.prod`, `.env.prod.db` ตามตัวอย่างใน repo

3. **Build และ Run ด้วย Docker**
    ```bash
    sudo docker-compose -f docker-compose.prod.yml up -d --build
    ```

4. **เข้าถึงระบบ**
    - เปิด browser ไปที่ `http://localhost:1337` (หรือ domain ที่ตั้งค่าไว้)

## โครงสร้างโปรเจกต์

- `services/web` : Flask backend
- `services/nginx` : Nginx config
- `docker-compose.prod.yml` : Compose สำหรับ production
- `docker-compose.yml` : Compose สำหรับ Development
- `README.md` : คำแนะนำการใช้งาน

## การร่วมพัฒนา

- Fork repo และสร้าง branch ของตัวเอง
- Pull Request พร้อมอธิบายการเปลี่ยนแปลง
- เขียน commit message ให้ชัดเจน
- ตรวจสอบ `.gitignore` ก่อน push

## License

MIT License