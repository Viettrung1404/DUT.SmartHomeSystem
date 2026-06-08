/**
 * Mock data for all Smart Home screens.
 * Vietnamese labels, realistic device/room structure.
 */

export interface User {
    id: string;
    name: string;
    email: string;
    avatar?: string;
}

export interface Home {
    id: string;
    name: string;
    address: string;
    roomCount: number;
    deviceCount: number;
    activeDevices: number;
}

export interface Room {
    id: string;
    homeId: string;
    name: string;
    icon: string;
    deviceCount: number;
    activeDevices: number;
    isOnline: boolean;
}

export type DeviceType =
    | 'light'
    | 'fan'
    | 'door'
    | 'buzzer'
    | 'distance_light'
    | 'temperature_humidity'
    | 'distance_sensor'
    | 'gas_sensor'
    | 'rain_sensor'
    | 'rain_servo';

export interface Device {
    id: string;
    roomId: string;
    name: string;
    type: DeviceType;
    icon: string;
    isOnline: boolean;
    isOn: boolean;
    brightness?: number;
    temperature?: number;
    humidity?: number;
    speed?: string;
    door?: string;
    distanceCm?: number;
    distanceAlert?: boolean;
    gasDetected?: boolean;
    rainDetected?: boolean;
}

export interface Automation {
    id: string;
    name: string;
    isEnabled: boolean;
    conditionSummary: string;
    actionSummary: string;
    icon: string;
    lastRun?: string;
}

export interface AIInsight {
    id: string;
    message: string;
    type: 'warning' | 'info' | 'suggestion';
    icon: string;
}

export interface SecurityAlert {
    id: string;
    message: string;
    timestamp: string;
    severity: 'low' | 'medium' | 'high';
    icon: string;
}

export interface ChatMessage {
    id: string;
    text: string;
    isUser: boolean;
    timestamp: string;
    deviceCard?: Device;
}

export const mockUser: User = {
    id: '1',
    name: 'Trung',
    email: 'trung@smarthome.vn',
};

export const mockHome: Home = {
    id: '1',
    name: 'Nhà Trung',
    address: '123 Nguyễn Huệ, Đà Nẵng',
    roomCount: 6,
    deviceCount: 24,
    activeDevices: 8,
};

export const mockRooms: Room[] = [
    { id: '1', homeId: '1', name: 'Phòng khách', icon: 'tv', deviceCount: 6, activeDevices: 3, isOnline: true },
    { id: '2', homeId: '1', name: 'Phòng ngủ', icon: 'moon', deviceCount: 4, activeDevices: 1, isOnline: true },
    { id: '3', homeId: '1', name: 'Nhà bếp', icon: 'coffee', deviceCount: 5, activeDevices: 2, isOnline: true },
    { id: '4', homeId: '1', name: 'Phòng tắm', icon: 'droplet', deviceCount: 3, activeDevices: 0, isOnline: true },
    { id: '5', homeId: '1', name: 'Ban công', icon: 'sun', deviceCount: 3, activeDevices: 1, isOnline: true },
    { id: '6', homeId: '1', name: 'Ga ra', icon: 'truck', deviceCount: 3, activeDevices: 1, isOnline: false },
];

export const mockDevices: Record<string, Device[]> = {
    '1': [
        { id: 'd1', roomId: '1', name: 'Đèn trần', type: 'light', icon: 'sun', isOnline: true, isOn: true, brightness: 80 },
        { id: 'd2', roomId: '1', name: 'Đèn bàn', type: 'light', icon: 'sun', isOnline: true, isOn: true, brightness: 60 },
        { id: 'd3', roomId: '1', name: 'Cảm biến nhiệt độ', type: 'temperature_humidity', icon: 'thermometer', isOnline: true, isOn: true, temperature: 28, humidity: 60 },
        { id: 'd4', roomId: '1', name: 'Cảm biến khoảng cách', type: 'distance_sensor', icon: 'radio', isOnline: true, isOn: true, distanceCm: 120 },
        { id: 'd5', roomId: '1', name: 'Mái che mưa', type: 'rain_servo', icon: 'droplet', isOnline: true, isOn: false },
        { id: 'd6', roomId: '1', name: 'Cảm biến mưa', type: 'rain_sensor', icon: 'cloud-rain', isOnline: true, isOn: false, rainDetected: false },
    ],
    '2': [
        { id: 'd7', roomId: '2', name: 'Đèn ngủ', type: 'light', icon: 'moon', isOnline: true, isOn: true, brightness: 30 },
        { id: 'd8', roomId: '2', name: 'Cảm biến nhiệt độ', type: 'temperature_humidity', icon: 'thermometer', isOnline: true, isOn: true, temperature: 26, humidity: 58 },
        { id: 'd9', roomId: '2', name: 'Quạt trần', type: 'fan', icon: 'loader', isOnline: true, isOn: false },
        { id: 'd10', roomId: '2', name: 'Cảm biến khoảng cách', type: 'distance_sensor', icon: 'radio', isOnline: true, isOn: true, distanceCm: 90 },
    ],
    '3': [
        { id: 'd11', roomId: '3', name: 'Đèn bếp', type: 'light', icon: 'sun', isOnline: true, isOn: true, brightness: 100 },
        { id: 'd12', roomId: '3', name: 'Máy hút mùi', type: 'fan', icon: 'wind', isOnline: true, isOn: true },
        { id: 'd13', roomId: '3', name: 'Cảm biến gas', type: 'gas_sensor', icon: 'alert-triangle', isOnline: true, isOn: true, gasDetected: false },
        { id: 'd14', roomId: '3', name: 'Đèn tủ bếp', type: 'light', icon: 'sun', isOnline: true, isOn: false, brightness: 0 },
        { id: 'd15', roomId: '3', name: 'Cảm biến mưa', type: 'rain_sensor', icon: 'cloud-rain', isOnline: false, isOn: false, rainDetected: false },
    ],
    '4': [
        { id: 'd16', roomId: '4', name: 'Đèn tắm', type: 'light', icon: 'sun', isOnline: true, isOn: false, brightness: 0 },
        { id: 'd17', roomId: '4', name: 'Quạt thông gió', type: 'fan', icon: 'wind', isOnline: true, isOn: false },
        { id: 'd18', roomId: '4', name: 'Cảm biến nhiệt độ', type: 'temperature_humidity', icon: 'thermometer', isOnline: true, isOn: true, temperature: 25, humidity: 70 },
    ],
    '5': [
        { id: 'd19', roomId: '5', name: 'Đèn ban công', type: 'light', icon: 'sun', isOnline: true, isOn: true, brightness: 50 },
        { id: 'd20', roomId: '5', name: 'Cảm biến nhiệt độ', type: 'temperature_humidity', icon: 'thermometer', isOnline: true, isOn: true, temperature: 30, humidity: 70 },
        { id: 'd21', roomId: '5', name: 'Mái che mưa ban công', type: 'rain_servo', icon: 'droplet', isOnline: true, isOn: false },
    ],
    '6': [
        { id: 'd22', roomId: '6', name: 'Đèn ga ra', type: 'light', icon: 'sun', isOnline: false, isOn: false, brightness: 0 },
        { id: 'd23', roomId: '6', name: 'Cửa ga ra', type: 'door', icon: 'door-open', isOnline: false, isOn: false, door: 'closed' },
        { id: 'd24', roomId: '6', name: 'Cảm biến khoảng cách', type: 'distance_sensor', icon: 'radio', isOnline: false, isOn: false, distanceCm: 0 },
    ],
};

export const mockAutomations: Automation[] = [
    { id: 'a1', name: 'Chế độ đi ngủ', isEnabled: true, conditionSummary: 'Sau 22:00', actionSummary: 'Tắt toàn bộ đèn, giảm AC xuống 24°C', icon: 'moon', lastRun: '22:00 hôm qua' },
    { id: 'a2', name: 'Chào buổi sáng', isEnabled: true, conditionSummary: 'Lúc 06:30', actionSummary: 'Bật đèn phòng khách, mở rèm', icon: 'sunrise', lastRun: '06:30 hôm nay' },
    { id: 'a3', name: 'Rời khỏi nhà', isEnabled: true, conditionSummary: 'Không phát hiện chuyển động 30 phút', actionSummary: 'Tắt tất cả thiết bị, khóa cửa', icon: 'log-out', lastRun: '08:15 hôm nay' },
    { id: 'a5', name: 'An ninh ban đêm', isEnabled: true, conditionSummary: 'Sau 23:00', actionSummary: 'Bật camera, khóa tất cả cửa', icon: 'shield', lastRun: '23:00 hôm qua' },
];

export const mockAIInsights: AIInsight[] = [
    { id: 'ai1', message: 'Phòng khách đang bật đèn 4 giờ liên tục. Bạn có muốn tắt không?', type: 'suggestion', icon: 'zap' },
    { id: 'ai3', message: 'Cửa trước chưa khóa. Khuyến nghị khóa ngay.', type: 'warning', icon: 'alert-triangle' },
];

export const mockSecurityAlerts: SecurityAlert[] = [
    { id: 's1', message: 'Cửa trước đã được mở', timestamp: '14:30', severity: 'medium', icon: 'door-open' },
    { id: 's2', message: 'Phát hiện chuyển động ở ban công', timestamp: '13:15', severity: 'low', icon: 'activity' },
    { id: 's3', message: 'Camera ga ra mất kết nối', timestamp: '12:00', severity: 'high', icon: 'wifi-off' },
    { id: 's4', message: 'Cửa sau đã khóa tự động', timestamp: '11:30', severity: 'low', icon: 'lock' },
    { id: 's5', message: 'Cảm biến khói kích hoạt nhẹ', timestamp: '10:45', severity: 'high', icon: 'alert-circle' },
];

export const mockChatMessages: ChatMessage[] = [
    { id: 'c1', text: 'Xin chào! Tôi có thể giúp gì cho bạn?', isUser: false, timestamp: '14:00' },
    { id: 'c2', text: 'Tắt đèn phòng ngủ', isUser: true, timestamp: '14:01' },
    { id: 'c3', text: 'Đã tắt đèn phòng ngủ cho bạn.', isUser: false, timestamp: '14:01' },
];

export const quickCommands = [
    'Tắt đèn phòng ngủ',
    'Bật máy lạnh 24°C',
    'Kích hoạt chế độ đi ngủ',
    'Mở rèm phòng khách',
    'Khóa tất cả cửa',
    'Tắt tất cả thiết bị',
];
