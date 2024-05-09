var bookedDates = {
    start: '2024-04-01',
    end: '2024-04-11'
  };

  // Функция для проверки, находится ли дата в забронированном диапазоне
  function isDateBooked(date) {
    var startDate = new Date(bookedDates.start);
    var endDate = new Date(bookedDates.end);
    var checkDate = new Date(date);
    return checkDate >= startDate && checkDate <= endDate;
  }

  // Получаем наши элементы ввода даты
  var startDateInput = document.getElementById('Start');
  var endDateInput = document.getElementById('End');

  // Функция, которая обрабатывает изменение даты начала
  startDateInput.addEventListener('change', function(event) {
    if (isDateBooked(startDateInput.value)) {
      alert('Эта дата уже забронирована. Пожалуйста, выберите другую дату.');
      startDateInput.value = ''; // Очистить выбор даты
    }
  });

  // Функция, которая обрабатывает изменение даты окончания
  endDateInput.addEventListener('change', function(event) {
    if (isDateBooked(endDateInput.value)) {
      alert('Эта дата уже забронирована. Пожалуйста, выберите другую дату.');
      endDateInput.value = ''; // Очистить выбор даты
    }
  });
  $(function() {
    var bookedDates = ["2024-01-10", "2024-02-15", "2024-03-20"]; // Пример забронированных дат в формате YYYY-MM-DD
  
    function highlightBookedDates(date) {
      var dateString = $.datepicker.formatDate('yy-mm-dd', date);
      if (bookedDates.indexOf(dateString) > -1) {
        return [true, 'bookedDate', 'Забронировано'];
      } else {
        return [true, '', ''];
      }
    }
  
    $('#datepicker').datepicker({
      beforeShowDay: highlightBookedDates
    });
  });
