import * as FileSystem from 'expo-file-system/legacy';

const LOG_DIR = FileSystem.documentDirectory ? `${FileSystem.documentDirectory}logs` : null;
const LOG_FILE = LOG_DIR ? `${LOG_DIR}/app.log` : null;

async function ensureLogDir() {
    if (!LOG_DIR) return;
    try {
        const info = await FileSystem.getInfoAsync(LOG_DIR);
        if (!info.exists) {
            await FileSystem.makeDirectoryAsync(LOG_DIR, { intermediates: true });
        }
    } catch {
        // Ignore file system errors on unsupported platforms.
    }
}

export async function logToFile(message: string) {
    if (!LOG_FILE) return;
    const timestamp = new Date().toISOString();
    const line = `${timestamp} ${message}\n`;
    try {
        await ensureLogDir();
        const currentContent = await FileSystem.readAsStringAsync(LOG_FILE).catch(() => '');
        await FileSystem.writeAsStringAsync(LOG_FILE, `${currentContent}${line}`, {
            encoding: FileSystem.EncodingType.UTF8,
        });
    } catch {
        // Ignore file system errors on unsupported platforms.
    }
}

export function logEvent(message: string) {
    console.log(message);
    void logToFile(message);
}
