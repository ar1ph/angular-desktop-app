import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DirSelectorComponent } from './dir-selector.component';

describe('DirSelectorComponent', () => {
  let component: DirSelectorComponent;
  let fixture: ComponentFixture<DirSelectorComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [DirSelectorComponent]
    });
    fixture = TestBed.createComponent(DirSelectorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
