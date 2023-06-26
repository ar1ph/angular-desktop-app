import { Component, ChangeDetectorRef } from '@angular/core';

declare var window: any;

@Component({
  selector: 'app-dir-selector',
  templateUrl: './dir-selector.component.html',
  styleUrls: ['./dir-selector.component.css'],
})
export class DirSelectorComponent {
  selectedPath: string = '';
  files: any[] = [];
  models: string[] = ['GPT-3', 'GPT-4', 'GPT-5'];
  strategies: string[] = ['l2', 'cosine', 'manhattan'];
  selectedModel = '';
  selectedStrategy = '';
  query = '';

  constructor(private cdr: ChangeDetectorRef) {}

  openDirectory() {
    window.electron.openDirectory();
  }

  displayFiles() {
    window.electron.displayFiles(this.selectedPath);
  }

  startBenchmark() {
    new window.Notification('Bencmark Started', {
      body: `Path: "${this.selectedPath}"
      Model: "${this.selectedModel}"
      Strategy: "${this.selectedStrategy}"
      Query: "${this.query}"
      `,
    });
  }

  ngOnInit() {
    window.electron.onDirectorySelected((path: any) => {
      this.selectedPath = path;
      this.cdr.detectChanges();
      this.displayFiles();
    });

    window.electron.onDirectoryFiles((content: any) => {
      this.files = content;
      this.cdr.detectChanges();
      new window.Notification('Content Read', {
        body: 'Directory has been read and the content can now be seen in the app',
      });
    });
  }

  ngOnDestroy() {
    window.electron.removeDirectorySelectedListener();
    window.electron.removeDirectoryFilesListener();
  }
}
