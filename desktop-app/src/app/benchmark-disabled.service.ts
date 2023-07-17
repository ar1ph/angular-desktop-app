import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class BenchmarkDisabledService {
  private benchmarkDisabledSubject = new BehaviorSubject<boolean>(false);
  benchmarkDisabled$ = this.benchmarkDisabledSubject.asObservable();

  setBenchmarkDisabled(status: boolean) {
    this.benchmarkDisabledSubject.next(status);
  }
}
