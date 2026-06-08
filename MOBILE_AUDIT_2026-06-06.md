# Mobile Audit - 2026-06-06

## Cap nhat sau fix

- Da fix backend cho `create device`, `suggestions auth`, `delete home`, `soft delete device`, `soft delete room`.
- Da fix mobile refresh-on-focus cho danh sach phong, chi tiet phong va danh sach automation.
- Da fix TypeScript blockers; `cd mobile && npx tsc --noEmit` hien pass.
- Da doi `automation/create` tu mock thanh luong tao that voi backend cho kich ban `time + toggle`.
- Da noi `settings` cho `logout` that va dieu huong vao quan ly nha/phong.
- Da fix `fileLogger` de hop voi `expo-file-system` cua Expo 54.
- Da bo cac icon Feather khong hop le nhu `door-open` o cac man hinh chinh.
- `cd mobile && npx expo export --platform web` pass sau cac thay doi moi.
- `cd mobile && npm run lint` pass nhung van con 25 warning cu, chu yeu la unused import va hook dependency.

## Pham vi

- Da doc README tong the, `backend/README.md`, `mobile/README.md`.
- Da ra soat cac man hinh mobile chinh: auth, dashboard, rooms, room detail, device detail, automation, security, suggestions, assistant, settings, quick actions.
- Da chay kiem tra tu dong:
  - `cd mobile && npm run lint`
  - `cd mobile && npx tsc --noEmit`
  - `cd mobile && npx expo export --platform web`
  - `cd backend && pytest`
- Da chay test API thuc te bang `FastAPI TestClient` tren backend local/PostgreSQL cho cac luong mobile dang goi: auth, homes, rooms, devices, automations, security, suggestions, websocket.

## Ket qua tong quan

### Hoat dong duoc trong muc do API/UI

- Dang ky, dang nhap, lay `/auth/me`: pass.
- Tao nha, danh sach nha, tao phong, danh sach phong: pass.
- Danh sach thiet bi, lay chi tiet thiet bi, toggle thiet bi, `set_angle` cho `rain_servo`: pass khi du lieu thiet bi da ton tai va `online`.
- Tao automation, bat/tat automation, danh sach automation: pass o backend.
- Tao security event, lay summary, lay danh sach event: pass o backend.
- WebSocket `/ws/home/{home_id}`: ket noi duoc khi co token, bi chan khi khong co token.
- `npx expo export --platform web`: pass, app van bundle duoc.

### Khong hoat dong / sai / can xu ly

1. Them thiet bi tu mobile dang hong hoan toan.
   - Mobile goi `devicesAPI.create(id, name, type)` tai `mobile/app/room/[id]/manage.tsx:66`.
   - Backend `Device` bat buoc `slug` va `mqtt_topic` tai `backend/src/entities/models.py:158` va `backend/src/entities/models.py:163`.
   - `create_device()` khong gan 2 truong nay tai `backend/src/apis/devices/service.py:23` va `backend/src/apis/devices/service.py:33`.
   - Test thuc te tra loi loi DB `null value in column "mqtt_topic"`.

2. Suggestions khong duoc auth dung.
   - Route `/suggestions/me` khong dung `CurrentUser`; dang dung placeholder `get_user_id_from_request()` tai `backend/src/apis/suggestions/controller.py:26`.
   - File con ghi TODO auth tai `backend/src/apis/suggestions/controller.py:22`.
   - Test thuc te: goi `/suggestions/me` khong token van `200`, goi co token cung tra cung payload.
   - Nghia la man hinh Suggestions co the hien du lieu cua user khac.

3. Automation create tren mobile chi la UI, khong luu xuong backend.
   - Man hinh wizard chi thay doi state local va ket thuc bang `router.back()` tai `mobile/app/automation/create.tsx:211`.
   - Khong co call `automationsAPI.create(...)` trong file nay.

4. Assistant screen chi la mock, khong goi AI/backend.
   - Response duoc gia lap bang `setTimeout(...)` tai `mobile/app/(tabs)/assistant.tsx:45-46`.
   - Khong co API call nao, nen tinh nang tro ly chua hoat dong thuc.

5. Settings screen chua co chuc nang that.
   - Cac menu item `onPress={() => { }}` tai `mobile/app/settings.tsx:75`.
   - Nut `Dang xuat` cung `onPress={() => { }}` tai `mobile/app/settings.tsx:97`.
   - Nghia la nguoi dung khong dang xuat duoc tu UI.

6. Security screen hien mot phan du lieu gia.
   - Du co goi `securityAPI.summary/events` tai `mobile/app/(tabs)/security.tsx:24-32`, phan cua/khoa va camera lai dung mock hardcode tai `mobile/app/(tabs)/security.tsx:55-62`.
   - Neu backend/device thay doi, 2 khu vuc nay van khong phan anh du lieu thuc.

7. Device type giua mobile va backend dang lech nhau.
   - Mobile room manage cho phep `['light', 'lock', 'camera', 'curtain', 'sensor', 'fan']` tai `mobile/app/room/[id]/manage.tsx:20`.
   - Backend enum chi co `LIGHT`, `FAN`, `AC`, `SENSOR`, `CAMERA`, `LOCK` tai `backend/src/entities/models.py:22-28`.
   - `curtain` tu mobile khong co trong enum backend.
   - Mobile device detail/room detail lai con xu ly cac type khac nhu `door`, `buzzer`, `distance_light`, `temperature_humidity`, `distance_sensor`, `gas_sensor`, `rain_sensor`, `rain_servo` tai `mobile/app/device/[id].tsx:38-81` va `mobile/app/room/[id].tsx:16-38`.
   - Hien tai he type va luong tao thiet bi chua thong nhat.

8. Fan speed command tra `200` nhung khong cap nhat speed.
   - Mobile goi `set_speed`.
   - Backend models co nhac den `set_speed` tai `backend/src/apis/devices/models.py:40-41`.
   - Nhưng `send_command()` khong xu ly `set_speed`; chi co `set_angle`, `set_position`, `lock/unlock`, `on/off`, `open/close` tai `backend/src/apis/devices/service.py:122-131`.
   - Test thuc te: goi `set_speed=weak` van tra metadata `speed: off`.

9. Trang thai cua/lock khong cap nhat day du.
   - Khi goi `open/close`, backend chi doi `power` tai `backend/src/apis/devices/service.py:129-131`, khong doi field `door`.
   - Test thuc te: command `open` tra `status=true` nhung metadata van `door: closed`.

10. Mobile chua xu ly tot type `lock`.
   - API tra type `LOCK` cho khoa.
   - Mapping icon o room/device detail khong co `lock` tai `mobile/app/room/[id].tsx:16-27` va `mobile/app/device/[id].tsx:38-49`.
   - UI dieu khien chuyen biet chi xu ly `door`, khong xu ly `lock` tai `mobile/app/device/[id].tsx:267` va `mobile/app/device/[id].tsx:412-420`.
   - Ket qua la khoa co nguy co hien icon sai va hien thi `Khac`.

11. Dashboard van hardcode thong tin.
   - Loi chao `Xin chao, Trung` tai `mobile/app/(tabs)/index.tsx:345`.
   - Thoi tiet `Da Nang • 30°C • Nhieu may` tai `mobile/app/(tabs)/index.tsx:375`.
   - Du login user nao cung khong doi.

12. Quick/auxiliary logging dang lech API Expo hien tai.
   - `expo-file-system` version `~19.0.22` tai `mobile/package.json:20`.
   - `mobile/utils/fileLogger.ts:3`, `:25`, `:26` dang dung `documentDirectory`, `EncodingType`, `append` ma `tsc` bao loi.
   - Hook websocket dang import logger nay, nen co rui ro loi runtime hoac phat sinh debt ky thuat.

13. TypeScript cua mobile dang fail.
   - `door-open` khong hop le trong Feather icon tai:
     - `mobile/app/room/[id].tsx:19`
     - `mobile/app/device/[id].tsx:41`
     - `mobile/app/automation/create.tsx:29`
   - `setType(device.type)` sai type tai `mobile/app/room/[id]/manage.tsx:84`.
   - `fileLogger` loi API tai `mobile/utils/fileLogger.ts:3`, `:25`, `:26`.
   - Lenh `npx tsc --noEmit` dang fail.

14. Backend test suite dang cu, khong chay duoc.
   - `backend/tests/conftest.py:8-10` import cac module khong con ton tai: `src.entities.user`, `src.entities.todo`, `src.auth.*`.
   - `pytest` fail ngay khi load `conftest.py`.

15. Xoa home qua API chua sach.
   - Test cleanup bang `DELETE /homes/{id}` bi fail vi FK voi `activity_logs`.
   - Can xem lai cascade/cleanup cho `activity_logs.home_id`.

## Ket qua lenh da chay

### `npm run lint`

- Pass voi warning, chua thay crash blocker.
- Nhieu warning ve unused import va `react-hooks/exhaustive-deps`.

### `npx tsc --noEmit`

- Fail.
- Nhom loi chinh:
  - icon `door-open` khong hop le
  - `setType(device.type)` sai type
  - `expo-file-system` API khong khop code hien tai

### `npx expo export --platform web`

- Pass.
- Bundle duoc tat ca route web/static.
- Dieu nay chi cho thay app bundle duoc, khong co nghia la cac feature business da dung.

### `pytest`

- Fail ngay luc load test config cu.

## Goi y uu tien xu ly

1. Sua backend create device de mobile them thiet bi duoc.
2. Khoa auth cho module suggestions va scope theo current user that.
3. Noi man hinh tao automation vao `automationsAPI.create`.
4. Quy hoach lai `device type` giua backend, mobile manage, room detail, device detail.
5. Sua `send_command()` cho `set_speed`, `door state`, va cac metadata ma UI dang doc.
6. Sua Settings logout/menu va bo mock trong Assistant/Security neu muon coi la feature hoan chinh.
7. Fix TypeScript va cap nhat `fileLogger` theo API `expo-file-system` hien tai.
8. Lam moi lai backend test suite.
