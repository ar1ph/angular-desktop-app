import {
  Component,
  ChangeDetectorRef,
  Input,
  Output,
  EventEmitter,
} from '@angular/core';
import { ViewChild } from '@angular/core';
import { MatTable } from '@angular/material/table';
import { BenchmarkDisabledService } from '../benchmark-disabled.service';

declare var window: any;

@Component({
  selector: 'app-benchmark-table',
  templateUrl: './benchmark-table.component.html',
  styleUrls: ['./benchmark-table.component.css'],
})
export class BenchmarkTableComponent {
  displayedColumns: string[] = [
    'Embedding Model',
    'DB Type',
    'Strategy',
    'Average k',
    'Sigma',
    'Frequency',
    'Queries',
  ];

  dataSource: any[] = [
    {
      'Embedding Model': 'TEST_ROW',
      'DB Type': 'Test',
      Strategy: 'test',
      'Average k': 4,
      Sigma: 1,
      Frequency: 3,
      Queries: 1,
    },
  ];

  @ViewChild(MatTable) table!: MatTable<any>;

  benchmarkDisabled = false;

  constructor(
    private cdr: ChangeDetectorRef,
    private benchmarkDisabledService: BenchmarkDisabledService
  ) {
    this.benchmarkDisabledService.benchmarkDisabled$.subscribe(
      (status: boolean) => {
        this.benchmarkDisabled = status;
      }
    );
  }
  ngOnInit() {
    window.electron.onBenchmarkData((message: any) => {
      this.benchmarkDisabledService.setBenchmarkDisabled(false);
      this.cdr.detectChanges();      let data = JSON.parse(message);
      console.log(data[0]);
      this.dataSource.push(data[0]);
      this.cdr.detectChanges();
      console.log(this.dataSource);
      new window.Notification('Benchmark Finished', {
        body: `Benchmark results can now be seen in the app. `,
      });
      this.table.renderRows();
      this.cdr.detectChanges();
    });
  }
}
