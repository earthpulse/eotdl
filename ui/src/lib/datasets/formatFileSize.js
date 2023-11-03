export default function formatFileSize(bytes) {
	if (bytes < 1024) {
		return bytes + " bytes";
	} else if (bytes < 104857) {
		return (bytes / 1024).toFixed(2) + " KB";
	} else if (bytes < 1073741824) {
		return (bytes / 1048576).toFixed(2) + " MB";
	} else {
		return (bytes / 1073741824).toFixed(2) + " GB";
	}
}