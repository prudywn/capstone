import json
import logging
from datetime import datetime
from metrics import record_dead_letter_message, ERRORS

logger = logging.getLogger(__name__)

class DeadLetterHandler:
    """Handles poisoned messages by sending them to a dead letter topic"""
    
    def __init__(self, kafka_producer=None, dead_letter_topic="air_quality_dead_letter"):
        self.kafka_producer = kafka_producer
        self.dead_letter_topic = dead_letter_topic
        
    def send_to_dead_letter(self, original_message, error_reason, city="unknown", pollutant=None):
        """Send a poisoned message to the dead letter topic"""
        try:
            dead_letter_message = {
                "timestamp": datetime.utcnow().isoformat(),
                "original_message": original_message,
                "error_reason": error_reason,
                "city": city,
                "pollutant": pollutant,
                "retry_count": 0
            }
            
            # In a real implementation, you would send to Kafka here
            # For now, we'll just log and record metrics
            logger.error(f"Message sent to dead letter topic: {error_reason} for {city}")
            logger.debug(f"Dead letter message: {json.dumps(dead_letter_message, indent=2)}")
            
            # Record metrics
            record_dead_letter_message(self.dead_letter_topic, error_reason)
            
            # If we had a Kafka producer, we would do:
            # if self.kafka_producer:
            #     self.kafka_producer.send(
            #         self.dead_letter_topic, 
            #         value=json.dumps(dead_letter_message).encode('utf-8')
            #     )
                
        except Exception as e:
            logger.error(f"Failed to send message to dead letter topic: {str(e)}")
            ERRORS.labels(error_type="dead_letter_failure", city=city).inc()
    
    def handle_validation_error(self, data, city, pollutant, error_details):
        """Handle validation errors by sending to dead letter topic"""
        self.send_to_dead_letter(
            original_message=data,
            error_reason=f"validation_error_{error_details}",
            city=city,
            pollutant=pollutant
        )
    
    def handle_processing_error(self, data, city, error_details):
        """Handle processing errors by sending to dead letter topic"""
        self.send_to_dead_letter(
            original_message=data,
            error_reason=f"processing_error_{error_details}",
            city=city
        )
    
    def handle_api_error(self, city, error_details):
        """Handle API errors by sending to dead letter topic"""
        self.send_to_dead_letter(
            original_message={"city": city, "error": error_details},
            error_reason=f"api_error_{error_details}",
            city=city
        )
