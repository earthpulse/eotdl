/**
 * Creates a hierarchical file tree structure from a flat list of files
 * @param {Array} files - Array of file objects with id property containing paths
 * @returns {Object} A tree structure representing the file hierarchy
 */
export function createFileTree(files) {
    const fileTree = {};

    for (const file of files) {
        const pathParts = file.id.split('/');
        let currentNode = fileTree;

        // Process each part of the path
        for (let i = 0; i < pathParts.length; i++) {
            const part = pathParts[i];
            const isFile = i === pathParts.length - 1;

            // Create the current node if it doesn't exist
            if (!currentNode[part]) {
                currentNode[part] = isFile ? { file } : { children: {} };
            } else if (!isFile && !currentNode[part].children) {
                // If it exists but doesn't have children, add children property
                currentNode[part].children = {};
            }

            // Move to the next level of the tree
            if (!isFile) {
                currentNode = currentNode[part].children;
            }
        }
    }

    return fileTree;
}

/**
 * Flattens a file tree into an array of path strings
 * @param {Object} tree - The file tree
 * @param {string} basePath - The base path to build upon
 * @returns {Array} An array of full file paths
 */
export function flattenFileTree(tree, basePath = '') {
    let paths = [];

    for (const key in tree) {
        const currentPath = basePath ? `${basePath}/${key}` : key;

        if (tree[key].file) {
            // This is a file
            paths.push(currentPath);
        }

        if (tree[key].children) {
            // This is a folder, recursively process children
            paths = paths.concat(flattenFileTree(tree[key].children, currentPath));
        }
    }

    return paths;
}