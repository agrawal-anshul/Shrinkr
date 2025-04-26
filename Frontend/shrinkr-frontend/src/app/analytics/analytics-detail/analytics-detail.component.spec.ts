import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AnalyticsDetailComponent } from './analytics-detail.component';

describe('AnalyticsDetailComponent', () => {
  let component: AnalyticsDetailComponent;
  let fixture: ComponentFixture<AnalyticsDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AnalyticsDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AnalyticsDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
