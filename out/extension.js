'use strict';
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = void 0;
const vscode = require("vscode");
const child_process_1 = require("child_process"); //
function runPythonScript(word) {
    return new Promise((resolve, reject) => {
        // 'inference-cpu.py' 파일의 경로를 정확히 지정해야 합니다.
        // 예를 들어, 현재 디렉토리에 있다고 가정하면 다음과 같이 쓸 수 있습니다.
        (0, child_process_1.exec)('/home/ysnamgoong42/miniconda3/envs/llama2/bin/python /home/ysnamgoong42/ws/vscode-extension-samples/document-editing-sample/inference-cpu.py --input_code "' + word + '"', (error, stdout, stderr) => {
            if (error) {
                vscode.window.showErrorMessage(`Error: ${error.message}`);
                return reject(error);
            }
            if (stderr) {
                vscode.window.showErrorMessage(`Stderr: ${stderr}`);
                return reject(new Error(stderr));
            }
            resolve(stdout.trim());
        });
    });
}
function activate(context) {
    const disposable = vscode.commands.registerCommand('extension.codeComment', async function () {
        // Get the active text editor
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            const document = editor.document;
            const selection = editor.selection;
            const word = document.getText(selection); // Get the word within the selection
            try {
                const pythonOutput = await runPythonScript(word);
                const newLineChar = '\n';
                // const reversed = word.split('').reverse().join('');
                editor.edit(editBuilder => {
                    editBuilder.replace(selection, word + newLineChar + "//" + pythonOutput);
                });
            }
            catch (error) {
                vscode.window.showErrorMessage('Python script execution failed.');
            }
        }
    });
    context.subscriptions.push(disposable);
}
exports.activate = activate;
//# sourceMappingURL=extension.js.map